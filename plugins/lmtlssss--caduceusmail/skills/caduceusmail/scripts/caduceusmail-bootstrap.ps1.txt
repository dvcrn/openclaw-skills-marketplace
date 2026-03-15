#!/usr/bin/env pwsh
param(
  [Parameter(Mandatory = $true)][string]$TenantId,
  [Parameter(Mandatory = $true)][string]$ClientId,
  [Parameter(Mandatory = $true)][string]$OrganizationDomain,
  [string]$ExchangeOrg = "",
  [string]$AppDisplayName = "caduceusmail-fabric",
  [switch]$RotateClientSecret,
  [int]$SecretLifetimeDays = 365,
  [switch]$SetAcceptedDomainInternalRelay,
  [switch]$EnableAcceptedDomainMatchSubdomains,
  [ValidateSet("auto","browser","device")][string]$BootstrapAuthMode = "auto",
  [string]$BootstrapAdminUpn = "",
  [switch]$SimulateSignIn,
  [switch]$WriteEnv,
  [switch]$WriteSecrets,
  [string]$EnvPath = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($EnvPath)) {
  $EnvPath = Join-Path $HOME ".caduceusmail/.env"
}

function Write-Step {
  param([string]$Message)
  Write-Host "[☤ m365-bootstrap] $Message"
}

function Ensure-Module {
  param([Parameter(Mandatory = $true)][string]$Name)
  if (-not (Get-Module -ListAvailable -Name $Name)) {
    Write-Step "Installing PowerShell module: $Name"
    Install-Module -Name $Name -Scope CurrentUser -Force -AllowClobber
  }
  Import-Module $Name -Force
}

function Upsert-EnvFileValue {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$Key,
    [Parameter(Mandatory = $true)][string]$Value
  )
  $dir = Split-Path -Parent $Path
  if ($dir -and -not (Test-Path -LiteralPath $dir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
  }
  if (-not (Test-Path -LiteralPath $Path)) {
    Set-Content -LiteralPath $Path -Value "" -Encoding UTF8
  }
  $content = Get-Content -LiteralPath $Path -Raw -ErrorAction SilentlyContinue
  if ($null -eq $content) { $content = "" }
  $escaped = [Regex]::Escape($Key)
  $line = "$Key=$Value"
  if ($content -match "(?m)^$escaped=") {
    $new = [Regex]::Replace($content, "(?m)^$escaped=.*$", [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $line })
    Set-Content -LiteralPath $Path -Value $new -Encoding UTF8
  } else {
    Add-Content -LiteralPath $Path -Value $line -Encoding UTF8
  }
}


function Resolve-BootstrapAuthMode {
  param([string]$RequestedMode)
  $mode = (($RequestedMode | ForEach-Object { "$_" }) -join "").Trim().ToLowerInvariant()
  if ($mode -and $mode -ne "auto") {
    return $mode
  }

  $sshSignals = @($env.SSH_TTY, $env.SSH_CONNECTION, $env.SSH_CLIENT) | Where-Object {
    -not [string]::IsNullOrWhiteSpace($_)
  }
  if ($sshSignals.Count -gt 0) {
    return "device"
  }

  $sandboxHints = @($env.OPENCLAW_SANDBOX, $env.CONTAINER, $env.DOCKER_CONTAINER) | Where-Object {
    -not [string]::IsNullOrWhiteSpace($_)
  }
  if ($sandboxHints.Count -gt 0 -or $env.CI -eq "true") {
    return "device"
  }

  if (-not $IsWindows) {
    $hasGuiHint = (-not [string]::IsNullOrWhiteSpace($env.DISPLAY)) -or (-not [string]::IsNullOrWhiteSpace($env.WAYLAND_DISPLAY))
    if (-not $hasGuiHint) {
      return "device"
    }
  }

  return "browser"
}

function Connect-GraphBootstrap {
  param(
    [Parameter(Mandatory = $true)][string]$Tenant,
    [Parameter(Mandatory = $true)][string[]]$Scopes,
    [Parameter(Mandatory = $true)][string]$AuthMode
  )
  if ($AuthMode -eq "device") {
    Write-Step "Connecting to Microsoft Graph (device code on another device/browser)"
    $cmd = Get-Command Connect-MgGraph -ErrorAction Stop
    $graphArgs = @{
      TenantId = $Tenant
      Scopes = $Scopes
      NoWelcome = $true
    }
    if ($cmd.Parameters.ContainsKey("UseDeviceCode")) {
      $graphArgs["UseDeviceCode"] = $true
    } elseif ($cmd.Parameters.ContainsKey("UseDeviceAuthentication")) {
      $graphArgs["UseDeviceAuthentication"] = $true
    } else {
      throw "Installed Microsoft.Graph.Authentication module does not expose device code parameters"
    }
    Connect-MgGraph @graphArgs
    return
  }
  Write-Step "Connecting to Microsoft Graph (interactive admin sign-in)"
  Connect-MgGraph -TenantId $Tenant -Scopes $Scopes -NoWelcome
}

function Connect-ExchangeBootstrap {
  param(
    [Parameter(Mandatory = $true)][string]$AuthMode,
    [string]$AdminUpn = ""
  )
  if ($AuthMode -eq "device") {
    Write-Step "Connecting to Exchange Online (device code on another device/browser)"
    Connect-ExchangeOnline -Device -ShowBanner:$false
    return
  }
  if (-not [string]::IsNullOrWhiteSpace($AdminUpn)) {
    Write-Step "Connecting to Exchange Online (interactive admin sign-in for $AdminUpn)"
    Connect-ExchangeOnline -UserPrincipalName $AdminUpn -ShowBanner:$false
    return
  }
  Write-Step "Connecting to Exchange Online (interactive admin sign-in)"
  Connect-ExchangeOnline -ShowBanner:$false
}

function Ensure-AppRoleAssignments {
  param(
    [Parameter(Mandatory = $true)]$PrincipalSp,
    [Parameter(Mandatory = $true)][string]$ResourceAppId,
    [Parameter(Mandatory = $true)][string[]]$RoleValues
  )
  $res = Get-MgServicePrincipal -Filter "appId eq '$ResourceAppId'" -ConsistencyLevel eventual
  if (-not $res -or $res.Count -lt 1) {
    throw "Could not resolve resource service principal for appId=$ResourceAppId"
  }
  $resourceSp = $res[0]
  $existing = Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $PrincipalSp.Id -All
  foreach ($rv in $RoleValues) {
    $role = $resourceSp.AppRoles | Where-Object {
      $_.Value -eq $rv -and $_.AllowedMemberTypes -contains "Application"
    } | Select-Object -First 1
    if (-not $role) {
      Write-Step "Role '$rv' not found on resource appId=$ResourceAppId (skipped)"
      continue
    }
    $already = $existing | Where-Object {
      $_.ResourceId -eq $resourceSp.Id -and $_.AppRoleId -eq $role.Id
    } | Select-Object -First 1
    if ($already) {
      Write-Step "App role already granted: $rv"
      continue
    }
    Write-Step "Granting app role: $rv"
    New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $PrincipalSp.Id -BodyParameter @{
      principalId = $PrincipalSp.Id
      resourceId  = $resourceSp.Id
      appRoleId   = $role.Id
    } | Out-Null
  }
}

function Ensure-ExchangeServicePrincipal {
  param(
    [Parameter(Mandatory = $true)][string]$ClientIdIn,
    [Parameter(Mandatory = $true)][string]$ObjectIdIn,
    [Parameter(Mandatory = $true)][string]$DisplayNameIn
  )
  $sp = $null
  try {
    $sp = Get-ServicePrincipal -Identity $ClientIdIn -ErrorAction SilentlyContinue
  } catch {
    $sp = $null
  }
  if (-not $sp) {
    Write-Step "Creating Exchange service principal pointer"
    New-ServicePrincipal -AppId $ClientIdIn -ObjectId $ObjectIdIn -DisplayName $DisplayNameIn | Out-Null
  } else {
    Write-Step "Exchange service principal pointer already exists"
  }
}

function Ensure-ExchangeRbacRole {
  param(
    [Parameter(Mandatory = $true)][string]$ClientIdIn,
    [Parameter(Mandatory = $true)][string]$RoleName
  )
  $existing = @()
  try {
    $existing = Get-ManagementRoleAssignment -App $ClientIdIn -Role $RoleName -ErrorAction SilentlyContinue
  } catch {
    $existing = @()
  }
  if ($existing -and $existing.Count -gt 0) {
    Write-Step "Exchange RBAC role already granted: $RoleName"
    return
  }
  $suffix = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
  $name = "caduceusmail-$($RoleName.Replace(' ','-').ToLower())-$suffix"
  Write-Step "Granting Exchange RBAC role: $RoleName"
  New-ManagementRoleAssignment -Name $name -App $ClientIdIn -Role $RoleName | Out-Null
}

function Set-AcceptedDomainPreferences {
  param(
    [Parameter(Mandatory = $true)][string]$DomainName,
    [bool]$SetInternalRelay,
    [bool]$MatchSubdomains
  )
  if ($SetInternalRelay) {
    Write-Step "Setting accepted domain DomainType=InternalRelay on $DomainName"
    Set-AcceptedDomain -Identity $DomainName -DomainType InternalRelay | Out-Null
  }
  if ($MatchSubdomains) {
    Write-Step "Setting accepted domain MatchSubdomains=true on $DomainName"
    Set-AcceptedDomain -Identity $DomainName -MatchSubdomains $true | Out-Null
  }
  $state = Get-AcceptedDomain -Identity $DomainName | Select-Object Name, DomainName, DomainType, MatchSubdomains, OutboundOnly
  return $state
}

$exchangeOrganization = if ([string]::IsNullOrWhiteSpace($ExchangeOrg)) { $OrganizationDomain } else { $ExchangeOrg }
$resolvedAuthMode = Resolve-BootstrapAuthMode -RequestedMode $BootstrapAuthMode

$summary = [ordered]@{
  ok = $false
  toolVersion = "5.3.3"
  tenantId = $TenantId
  clientId = $ClientId
  organizationDomain = $OrganizationDomain
  exchangeOrg = $exchangeOrganization
  steps = @()
  generatedSecret = $null
  exchangeAuthorization = @()
  acceptedDomainState = $null
  sign_in_events = if ($resolvedAuthMode -eq "device") { 2 } else { 1 }
  sso_mode = if ($resolvedAuthMode -eq "device") { "device_code_expected" } else { "single_sign_on_expected" }
  bootstrapAuthMode = $resolvedAuthMode
  bootstrapAdminUpn = $BootstrapAdminUpn
}

if ($SimulateSignIn) {
  $summary.ok = $true
  $summary.steps = @("simulation_mode", "graph_connected_simulated", "exchange_connected_simulated", "exchange_rbac_ready_simulated")
  $summary.exchangeAuthorization = @(
    @{ RoleName = "Application Mail.Send"; AllowedResourceScope = "Organization"; ScopeType = "Organization"; InScope = "Simulated" },
    @{ RoleName = "Application Mail.ReadWrite"; AllowedResourceScope = "Organization"; ScopeType = "Organization"; InScope = "Simulated" },
    @{ RoleName = "Mail Recipients"; AllowedResourceScope = "Organization"; ScopeType = "Organization"; InScope = "Simulated" }
  )
  $summary | ConvertTo-Json -Depth 8
  exit 0
}

try {
  Ensure-Module -Name "Microsoft.Graph.Authentication"
  Ensure-Module -Name "Microsoft.Graph.Applications"
  Ensure-Module -Name "ExchangeOnlineManagement"
  $summary.steps += "modules_ready"

  $bootstrapScopes = @(
    "Application.ReadWrite.All",
    "AppRoleAssignment.ReadWrite.All",
    "Directory.Read.All",
    "Organization.Read.All"
  )
  Connect-GraphBootstrap -Tenant $TenantId -Scopes $bootstrapScopes -AuthMode $resolvedAuthMode
  Select-MgProfile -Name "v1.0"
  $summary.steps += "graph_connected"

  $apps = Get-MgApplication -Filter "appId eq '$ClientId'" -ConsistencyLevel eventual
  if (-not $apps -or $apps.Count -lt 1) {
    throw "App registration not found for ClientId=$ClientId"
  }
  $app = $apps[0]
  $summary.steps += "app_registration_resolved"

  $sps = Get-MgServicePrincipal -Filter "appId eq '$ClientId'" -ConsistencyLevel eventual
  $principalSp = if ($sps -and $sps.Count -ge 1) { $sps[0] } else { $null }
  if (-not $principalSp) {
    Write-Step "Creating service principal for app"
    $principalSp = New-MgServicePrincipal -AppId $ClientId
  }
  $summary.steps += "service_principal_ready"

  Ensure-AppRoleAssignments -PrincipalSp $principalSp -ResourceAppId "00000003-0000-0000-c000-000000000000" -RoleValues @(
    "Mail.Send",
    "Mail.ReadWrite",
    "User.Read.All",
    "Domain.ReadWrite.All",
    "Directory.Read.All",
    "Organization.Read.All"
  )
  $summary.steps += "graph_app_roles_ready"

  Ensure-AppRoleAssignments -PrincipalSp $principalSp -ResourceAppId "00000002-0000-0ff1-ce00-000000000000" -RoleValues @(
    "Exchange.ManageAsApp"
  )
  $summary.steps += "exchange_api_role_ready"

  if ($RotateClientSecret) {
    $expiresAt = (Get-Date).ToUniversalTime().AddDays([Math]::Max(1, $SecretLifetimeDays))
    $cred = Add-MgApplicationPassword -ApplicationId $app.Id -PasswordCredential @{
      displayName = "caduceusmail-auto-" + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
      endDateTime = $expiresAt
    }
    if ($cred -and $cred.SecretText) {
      $summary.generatedSecret = @{
        value = $cred.SecretText
        endDateTime = $expiresAt.ToString("o")
      }
      $summary.steps += "client_secret_rotated"
    }
  }

  Connect-ExchangeBootstrap -AuthMode $resolvedAuthMode -AdminUpn $BootstrapAdminUpn
  $summary.steps += "exchange_connected"

  Ensure-ExchangeServicePrincipal -ClientIdIn $ClientId -ObjectIdIn $principalSp.Id -DisplayNameIn $AppDisplayName
  $summary.steps += "exchange_service_principal_ready"

  Ensure-ExchangeRbacRole -ClientIdIn $ClientId -RoleName "Application Mail.Send"
  Ensure-ExchangeRbacRole -ClientIdIn $ClientId -RoleName "Application Mail.ReadWrite"
  Ensure-ExchangeRbacRole -ClientIdIn $ClientId -RoleName "Mail Recipients"
  $summary.steps += "exchange_rbac_ready"

  try {
    $authRows = Test-ServicePrincipalAuthorization -Identity $ClientId | Select-Object RoleName, AllowedResourceScope, ScopeType, InScope
    $summary.exchangeAuthorization = @($authRows)
  } catch {
    $summary.exchangeAuthorization = @(@{ error = $_.Exception.Message })
  }

  if ($SetAcceptedDomainInternalRelay -or $EnableAcceptedDomainMatchSubdomains) {
    $state = Set-AcceptedDomainPreferences -DomainName $OrganizationDomain -SetInternalRelay:$SetAcceptedDomainInternalRelay -MatchSubdomains:$EnableAcceptedDomainMatchSubdomains
    $summary.acceptedDomainState = $state
    $summary.steps += "accepted_domain_preferences_applied"
  }

  if ($WriteEnv) {
    Upsert-EnvFileValue -Path $EnvPath -Key "ENTRA_TENANT_ID" -Value $TenantId
    Upsert-EnvFileValue -Path $EnvPath -Key "ENTRA_CLIENT_ID" -Value $ClientId
    Upsert-EnvFileValue -Path $EnvPath -Key "EXCHANGE_ORGANIZATION" -Value $exchangeOrganization
    if ($WriteSecrets -and $summary.generatedSecret -and $summary.generatedSecret.value) {
      Upsert-EnvFileValue -Path $EnvPath -Key "ENTRA_CLIENT_SECRET" -Value ([string]$summary.generatedSecret.value)
    }
    $summary.steps += "env_written"
  }

  $summary.ok = $true
}
catch {
  $summary.ok = $false
  $summary.error = $_.Exception.Message
}
finally {
  try { Disconnect-ExchangeOnline -Confirm:$false | Out-Null } catch {}
  try { Disconnect-MgGraph | Out-Null } catch {}
}

$summary | ConvertTo-Json -Depth 8
