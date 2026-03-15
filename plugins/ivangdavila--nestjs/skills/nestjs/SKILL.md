---
name: NestJS
description: "Avoid common NestJS mistakes — DI scoping, circular dependencies, validation pipes, and module organization traps."
---

## Dependency Injection
- Provider not available — must be in `providers` array AND `exports` if used by other modules
- Circular dependency crashes — use `forwardRef(() => Module)` in both modules
- Default scope is singleton — same instance across requests, careful with state
- Request-scoped provider — `@Injectable({ scope: Scope.REQUEST })`, propagates to dependents

## Module Organization
- Import module, not provider directly — `imports: [UserModule]` not `providers: [UserService]`
- `exports` makes providers available to importers — without it, provider stays private
- Global modules need `@Global()` decorator — only for truly shared (config, logger)
- `forRoot()` vs `forRootAsync()` — async for when config depends on other providers

## Validation
- `ValidationPipe` needs `class-validator` decorators — plain classes won't validate
- Enable `transform: true` for auto-transformation — string `"1"` to number `1`
- `whitelist: true` strips unknown properties — `forbidNonWhitelisted: true` to error instead
- Nested objects need `@ValidateNested()` AND `@Type(() => NestedDto)` — both required

## Execution Order
- Middleware → Guards → Interceptors (pre) → Pipes → Handler → Interceptors (post) → Filters
- Guards can't access transformed body — run before pipes
- Global pipes run before route pipes — but after guards
- Exception filters catch errors from entire chain — including guards and pipes

## Exception Handling
- `throw new HttpException()` not `return` — must throw for filter to catch
- Custom exceptions extend `HttpException` — or implement `ExceptionFilter`
- Unhandled exceptions become 500 — wrap external calls in try/catch
- Built-in exceptions: `BadRequestException`, `NotFoundException`, etc. — use these, not generic HttpException

## Testing
- `createTestingModule` doesn't auto-mock — provide mocks explicitly in `providers`
- Override with `.overrideProvider(X).useValue(mock)` — before `.compile()`
- E2E tests need `app.init()` — and `app.close()` in afterAll
- Request-scoped providers complicate unit tests — consider making them singleton when possible

## Common Mistakes
- `@Body()` without DTO returns plain object — no validation, no transformation
- `@Param('id')` is always string — use `ParseIntPipe` for number: `@Param('id', ParseIntPipe)`
- Guards returning false gives 403 — throw specific exception for better error messages
- Async providers need factory — `useFactory: async () => await createConnection()`
- Forgetting `await` on async service methods — returns Promise, not value
