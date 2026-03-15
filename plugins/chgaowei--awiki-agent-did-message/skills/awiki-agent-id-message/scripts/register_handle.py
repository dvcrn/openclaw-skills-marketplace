"""Register a Handle (human-readable DID alias) interactively.

Usage:
    # Register a Handle (will prompt for OTP)
    uv run python scripts/register_handle.py --handle alice --phone +8613800138000

    # With invite code (for short handles <= 4 chars)
    uv run python scripts/register_handle.py --handle bob --phone +8613800138000 --invite-code ABC123

    # Specify credential name
    uv run python scripts/register_handle.py --handle alice --phone +8613800138000 --credential myhandle

[INPUT]: SDK (handle registration, OTP), credential_store (save identity),
         logging_config
[OUTPUT]: Register Handle + DID identity and save credentials
[POS]: Interactive CLI for Handle registration

[PROTOCOL]:
1. Update this header when logic changes
2. Check the folder's CLAUDE.md after updating
"""

import argparse
import asyncio
import logging
import sys

from utils import SDKConfig, create_user_service_client, send_otp, register_handle
from utils.logging_config import configure_logging
from credential_store import save_identity

logger = logging.getLogger(__name__)


async def do_register(
    handle: str,
    phone: str,
    otp_code: str | None = None,
    invite_code: str | None = None,
    name: str | None = None,
    credential_name: str = "default",
) -> None:
    """Register a Handle interactively."""
    logger.info(
        "Registering handle handle=%s credential=%s invite_code_present=%s",
        handle,
        credential_name,
        bool(invite_code),
    )
    config = SDKConfig()
    print(f"Service configuration:")
    print(f"  user-service: {config.user_service_url}")
    print(f"  DID domain  : {config.did_domain}")

    async with create_user_service_client(config) as client:
        # 1. Send OTP if not provided
        if otp_code is None:
            print(f"\nSending OTP to {phone}...")
            await send_otp(client, phone)
            print("OTP sent. Check your phone.")
            otp_code = input("Enter OTP code: ").strip()
            if not otp_code:
                print("OTP code is required.")
                sys.exit(1)

        # 2. Register Handle
        print(f"\nRegistering Handle '{handle}'...")
        identity = await register_handle(
            client=client,
            config=config,
            phone=phone,
            otp_code=otp_code,
            handle=handle,
            invite_code=invite_code,
            name=name or handle,
            is_public=True,
        )

        print(f"  Handle    : {handle}.{config.did_domain}")
        print(f"  DID       : {identity.did}")
        print(f"  unique_id : {identity.unique_id}")
        print(f"  user_id   : {identity.user_id}")
        print(f"  JWT token : {identity.jwt_token[:50]}...")

        # 3. Save credential
        path = save_identity(
            did=identity.did,
            unique_id=identity.unique_id,
            user_id=identity.user_id,
            private_key_pem=identity.private_key_pem,
            public_key_pem=identity.public_key_pem,
            jwt_token=identity.jwt_token,
            display_name=name or handle,
            handle=handle,
            name=credential_name,
            did_document=identity.did_document,
            e2ee_signing_private_pem=identity.e2ee_signing_private_pem,
            e2ee_agreement_private_pem=identity.e2ee_agreement_private_pem,
        )
        print(f"\nCredential saved to: {path}")
        print(f"Credential name: {credential_name}")


def main() -> None:
    configure_logging(console_level=None, mirror_stdio=True)

    parser = argparse.ArgumentParser(description="Register a Handle (human-readable DID alias)")
    parser.add_argument("--handle", required=True, type=str,
                        help="Handle local-part (e.g., alice)")
    parser.add_argument("--phone", required=True, type=str,
                        help="Phone number in international format with country code "
                             "(e.g., +8613800138000 for China, +14155552671 for US). "
                             "China local 11-digit numbers are auto-prefixed with +86.")
    parser.add_argument("--otp-code", type=str, default=None,
                        help="OTP code (if already obtained; otherwise will send and prompt)")
    parser.add_argument("--invite-code", type=str, default=None,
                        help="Invite code (required for short handles <= 4 chars)")
    parser.add_argument("--name", type=str, default=None,
                        help="Display name (defaults to handle)")
    parser.add_argument("--credential", type=str, default="default",
                        help="Credential storage name (default: default)")

    args = parser.parse_args()
    logger.info(
        "register_handle CLI started handle=%s credential=%s",
        args.handle,
        args.credential,
    )
    asyncio.run(do_register(
        handle=args.handle,
        phone=args.phone,
        otp_code=args.otp_code,
        invite_code=args.invite_code,
        name=args.name,
        credential_name=args.credential,
    ))


if __name__ == "__main__":
    main()
