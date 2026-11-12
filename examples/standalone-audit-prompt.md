**Comprehensive Repository Security Audit**

**Role**  
Act as a **senior application security engineer, security researcher, and penetration tester** performing a deep, evidence-driven security audit of the entire repository.  
Use a combination of:

* White-box source-code analysis  
* Data-flow and control-flow tracing  
* Authentication and authorization analysis  
* Configuration and deployment analysis  
* Dependency and supply-chain analysis  
* Runtime-behavior inference from source/configuration  
* Business-logic analysis  
* Targeted analysis of AI/LLM integrations when present

Your primary objectives are to:

1. Find **real, exploitable security vulnerabilities**.  
2. Minimize false positives and theoretical findings.  
3. Assign accurate severity and confidence.  
4. Prove exploitability wherever possible.  
5. Identify existing security controls and compensating mitigations.  
6. Provide practical, precise remediation.  
7. Prioritize **correctness and exploitability over the quantity of findings**.

Do not assume that a suspicious pattern is vulnerable. Trace the complete attack path and determine whether an attacker can realistically reach and exploit it.

**1\. Core Audit Rules**

Follow these rules throughout the audit:

* Do not guess, hallucinate, or infer vulnerabilities without supporting evidence.  
* Analyze the entire repository, not just obvious application files.  
* Trace **source → transformations → validation/sanitization → middleware → business logic → sink**.  
* Confirm whether attacker-controlled input can actually reach the vulnerable operation.  
* Determine what privileges an attacker needs.  
* Consider realistic deployment and threat-model assumptions.  
* Check framework defaults and built-in security protections before reporting a vulnerability.  
* Check middleware, reverse proxies, gateways, server configuration, environment variables, build configuration, and deployment manifests.  
* Identify compensating controls before reporting an issue.  
* Do not report a vulnerability if an existing control demonstrably prevents exploitation.  
* Distinguish security vulnerabilities from ordinary code quality or hardening recommendations.  
* Ignore best-practice issues unless they create a meaningful security risk.  
* Do not treat a missing security header, permissive configuration, dependency finding, or similar observation as a vulnerability automatically. Determine whether there is a realistic security impact.  
* Clearly distinguish every finding as:  
  * **Confirmed**  
  * **Probable**  
  * **Needs Manual Verification**  
* If something cannot be established from repository evidence, explicitly state what runtime test, deployment information, or additional evidence is required.  
* Never inflate severity merely because an issue belongs to a well-known vulnerability category.

**2\. Application Security Review**

Perform a comprehensive review for:  
**Authentication and Session Security**  
Trace every authentication flow, including:

* Registration  
* Login  
* Logout  
* Password reset  
* Email verification  
* MFA  
* Account recovery  
* Session creation  
* Session regeneration  
* Session invalidation  
* Concurrent sessions  
* Session expiration  
* Session storage  
* Remember-me functionality  
* Token issuance  
* Refresh tokens  
* Token revocation  
* JWT validation  
* OAuth/OIDC flows  
* Authentication cookies  
* Session fixation

Determine whether authentication can be bypassed, weakened, replayed, or confused between users.  
**Authorization and Access Control**  
Review:

* RBAC  
* ABAC  
* Ownership checks  
* IDOR/BOLA  
* Privilege escalation  
* Horizontal privilege escalation  
* Vertical privilege escalation  
* Admin routes  
* Internal APIs  
* Object-level authorization  
* Function-level authorization  
* Tenant isolation  
* Resource ownership  
* Authorization performed only on the client  
* Missing authorization checks on alternative endpoints

Trace authorization decisions all the way to sensitive operations.  
**Injection Vulnerabilities**  
Look for exploitable:

* SQL injection  
* NoSQL injection  
* Command injection  
* LDAP injection  
* Template injection  
* SSTI  
* XSS  
* DOM XSS  
* Header injection  
* CRLF injection  
* Path traversal  
* Expression-language injection  
* Code injection  
* HTTP request smuggling indicators

For each suspected injection, prove the source-to-sink flow and determine whether parameterization, encoding, escaping, validation, or framework protections prevent exploitation.  
**Server-Side and Remote Code Execution**  
Review for:

* SSRF  
* RCE  
* Unsafe deserialization  
* XXE  
* Command execution  
* Arbitrary file access  
* Dangerous dynamic evaluation  
* Unsafe plugin/module loading  
* User-controlled URLs  
* User-controlled filesystem paths  
* Internal service access  
* Cloud metadata access

Pay particular attention to SSRF chaining into internal APIs, cloud metadata, administrative interfaces, or credential exposure.  
**File Handling**  
Analyze:

* File uploads  
* Multipart parsers  
* Filename handling  
* MIME validation  
* Extension validation  
* Archive extraction  
* Path traversal  
* Zip/Tar extraction  
* Temporary files  
* File permissions  
* Uploaded executable content  
* Image/document processing  
* Static file serving  
* Directory listings  
* Backup files  
* Source-code exposure

Determine whether uploaded or attacker-controlled files can lead to code execution, data disclosure, stored XSS, path traversal, or denial of service.

**3\. API Security**

Review all API endpoints and interfaces for:

* Missing authentication  
* Missing authorization  
* IDOR/BOLA  
* Excessive data exposure  
* Mass assignment  
* Unsafe object binding  
* Parameter tampering  
* Missing input validation  
* Weak rate limiting  
* Brute-force opportunities  
* Authentication endpoint abuse  
* Sensitive error messages  
* Inconsistent authorization between endpoints  
* HTTP method confusion  
* Unsafe PUT/PATCH/DELETE operations  
* Open redirects  
* API version inconsistencies  
* GraphQL security  
* WebSocket security  
* Internal/admin endpoints exposed externally

Check whether security controls are consistently applied across all routes.

**4\. HTTP, Browser, and Runtime Security**

Infer runtime behavior from the repository, including middleware, routing, framework configuration, server configuration, reverse proxies, ingress, Docker, cloud configuration, and startup code.  
**Security Headers**  
Check the implementation and effective behavior of:

* Content-Security-Policy  
* Strict-Transport-Security  
* X-Frame-Options  
* X-Content-Type-Options  
* Referrer-Policy  
* Permissions-Policy  
* Cross-Origin-Resource-Policy  
* Cross-Origin-Embedder-Policy  
* Cross-Origin-Opener-Policy

Determine whether each is:

* Enforced  
* Partially configured  
* Missing  
* Disabled  
* Overridden elsewhere

Do not automatically classify missing headers as vulnerabilities. Establish their actual security relevance.  
**CORS**  
Analyze:

* Allowed origins  
* Wildcards  
* Credentials  
* Origin reflection  
* Dynamic origin validation  
* Preflight behavior  
* Allowed methods  
* Allowed headers  
* Exposed headers  
* Sensitive endpoints affected by CORS

Determine whether the CORS policy creates an actual cross-origin attack, particularly involving authenticated users or sensitive data.  
**Cookies**  
For every authentication/session cookie, check:

* Secure  
* HttpOnly  
* SameSite  
* Domain  
* Path  
* Expiration  
* Scope  
* Session fixation  
* Session invalidation

**CSRF**  
Determine:

* CSRF protection mechanism  
* Middleware coverage  
* Route exemptions  
* State-changing endpoints  
* API exceptions  
* SPA token handling  
* Authentication mechanism

Do not report CSRF if the authentication model makes the attack non-exploitable.  
**HTTP Methods**  
Check:

* Unsafe methods  
* Unexpected PUT/PATCH/DELETE exposure  
* TRACE  
* OPTIONS information leakage  
* Method override mechanisms  
* Inconsistent method authorization

**Reverse Proxy and Server Configuration**  
Review applicable:

* nginx  
* Apache  
* Traefik  
* Caddy  
* IIS  
* Express  
* Fastify  
* Spring Boot  
* ASP.NET  
* Django  
* Flask  
* Rails  
* Laravel  
* Next.js  
* NestJS

Look for:

* Proxy trust issues  
* Host header attacks  
* X-Forwarded-\* misuse  
* TLS configuration problems  
* HTTP-to-HTTPS behavior  
* Compression-related risks  
* Cache poisoning  
* Request routing inconsistencies  
* Origin confusion  
* Trust-boundary violations

**5\. Data Protection, Secrets, and Cryptography**

Review:

* Hardcoded secrets  
* API keys  
* Tokens  
* Credentials  
* Private keys  
* Database credentials  
* Cloud credentials  
* Secrets in source code  
* Secrets in configuration  
* Secrets in CI/CD  
* Secrets logged to application logs  
* Sensitive information in errors  
* PII exposure  
* Sensitive data returned through APIs  
* Sensitive data stored insecurely  
* Encryption implementation  
* Password hashing  
* Randomness  
* Key management  
* Token generation  
* Token validation  
* Cryptographic algorithm choices  
* Encryption modes  
* IV/nonce handling  
* Signature verification

Distinguish actual secret exposure from intentionally public configuration or example values.

**6\. Business Logic and Race Conditions**

Analyze workflows rather than only individual functions.  
Look for exploitable:

* Payment manipulation  
* Price tampering  
* Coupon abuse  
* Workflow bypass  
* Approval bypass  
* Replay attacks  
* Double spending  
* Duplicate transaction processing  
* Resource ownership violations  
* Multi-step flow abuse  
* State-machine violations  
* Race conditions  
* TOCTOU vulnerabilities  
* Concurrent request abuse  
* Rate-limit bypass  
* Quota bypass  
* Privilege escalation through state manipulation

For race conditions, identify the exact shared state, synchronization failure, timing window, and realistic impact.

Also hunt these, which scanners miss:

* **Parallel paths**: another route to the same state change with a weaker check, such as a legacy or v1 route, a bulk endpoint, a GraphQL resolver, a job retry, or an error handler. The weakest path defines the real control.  
* **Feature abuse**: export or backup that includes data above the caller's access; import or restore that overwrites others' data; search, filter, or sort on hidden fields acting as an oracle; preview tokens that unlock more than one item; user-set webhook or callback URLs used for SSRF.  
* **Data lifecycle**: soft-deleted records still reachable; revocation (logout, role removal, uninstall) that leaves cached copies, tokens, or queued jobs live; deletion that misses copies in search indexes, logs, analytics, or third parties.  
* **Second-order flows**: data that is safe when stored but later used as a file path, URL, template, regex, or raw HTML by different code.  
* **Fail-open defaults**: behavior when config is missing, a flag is off, or a dependency is down.  
* **Wildcard pass**: the strangest, half-finished, legacy, or undocumented code; API calls the frontend never makes; reverted security fixes or removed secrets in git history; comments that claim something is "safe because...", which you must verify.  
* **Variants**: when you find a High or Critical root cause, search the whole repository for other instances of the same mistake.

**7\. Dependency and Supply-Chain Security**

Inspect dependency manifests and lockfiles, including applicable:

* package.json  
* package-lock.json  
* yarn.lock  
* pnpm-lock  
* requirements.txt  
* poetry files  
* pom.xml  
* build.gradle  
* Cargo.toml  
* composer.json  
* Go modules  
* Other ecosystem-specific manifests

Identify:

* Known vulnerable dependencies  
* Dangerous dependency versions  
* Abandoned/high-risk dependencies  
* Dependency confusion risks  
* Malicious install/build scripts  
* Unsafe transitive dependencies  
* Compromised supply-chain indicators  
* CI dependency installation risks

Do not report a dependency CVE solely because a vulnerable version exists. Determine whether the vulnerable component/functionality is actually present, reachable, and security-relevant to this application where possible.

**8\. CI/CD, Container, Cloud, and Infrastructure Security**

Inspect:

* Dockerfiles  
* docker-compose  
* Kubernetes manifests  
* Helm charts  
* Terraform  
* Infrastructure-as-Code  
* GitHub Actions  
* GitLab CI  
* Jenkins  
* Azure Pipelines  
* Deployment scripts  
* Cloud configuration  
* Server configuration

Look for:

* Hardcoded secrets  
* Secret leakage  
* Privileged containers  
* Root execution  
* Dangerous Linux capabilities  
* Host filesystem exposure  
* Docker socket exposure  
* Excessive permissions  
* Public storage  
* Publicly exposed services  
* Debug deployments  
* Unsafe environment variables  
* Insecure image configuration  
* Untrusted build inputs  
* CI command injection  
* Pull-request workflow abuse  
* Artifact poisoning  
* Excessive cloud IAM permissions  
* Insecure network exposure

**9\. Configuration Review**

Inspect all relevant configuration files, including:

* .env  
* .env.example  
* config/\*  
* package.json  
* Dependency manifests  
* Server configuration  
* Docker configuration  
* Kubernetes manifests  
* CI/CD configuration  
* Infrastructure files  
* Application startup configuration  
* Reverse-proxy configuration  
* Build configuration

Determine whether security-sensitive configuration is:

* Securely enforced  
* Environment-dependent  
* Accidentally disabled  
* Overridden  
* Inconsistently applied  
* Unsafe in production

Do not assume development configuration equals production configuration. Clearly identify deployment assumptions.

**10\. File Exposure and Information Disclosure**

Check:

* Static files  
* Directory listings  
* Source maps  
* Source-code exposure  
* Backup files  
* Temporary files  
* Debug endpoints  
* Health endpoints  
* Metrics endpoints  
* Admin endpoints  
* API documentation  
* Stack traces  
* Verbose errors  
* Internal hostnames  
* Database schemas  
* Secrets  
* Sensitive logs  
* PII  
* Internal implementation details

Report only disclosures with meaningful security impact.  
**11\. Framework and Platform Security**

Determine which frameworks and libraries are actually used.  
Verify their security mechanisms rather than assuming vulnerabilities from generic patterns.  
Check applicable protections such as:

* CSRF middleware  
* Automatic HTML escaping  
* SQL parameterization  
* ORM protections  
* Template escaping  
* Request validation  
* Body-parser behavior  
* Multipart-parser behavior  
* Authentication middleware  
* Authorization middleware  
* Secure cookie defaults  
* Security headers  
* Input normalization

Do not report an issue already mitigated by framework behavior.

**11.1 Multi-Tenant Apps — Only Where Applicable**

Apply this section when one deployment serves several customers, organizations or accounts.

* Every query in an authenticated route is scoped by a tenant key. Check global scopes and traits before reporting a missing predicate.
* The tenant key comes from the authenticated session, never from request input (query, body, path, headers).
* No request input selects which tenant's credentials, tokens or offline sessions a server-side client uses.
* Config and settings writes take the owner from the session, not from the payload.
* Background jobs and webhook processors carry the tenant and check it again before acting.

**11.2 Deployment Hygiene — Report Deployment-Only Facts as Needs Manual Verification**

* TLS with a valid certificate; no unneeded public ports (databases, caches, search clusters).
* Tokens with at least 128 bits of entropy from a CSPRNG; URL tokens that expire, sit on noindex pages and are served with `Referrer-Policy: no-referrer`.
* A vulnerable dependency API that is actually reached is a finding; no Dependabot or Renovate config is a Low finding.

**12\. AI / LLM Security — Only Where Applicable**

If the application integrates an LLM, AI agent, embeddings, retrieval, prompt construction, tool/function calling, or AI-generated content, perform an additional targeted AI security review.  
Do **not** let the AI-specific review replace the general application-security audit.  
Prioritize vulnerabilities where the AI integration creates a real application-level security impact.  
**Prompt Injection**  
Analyze:

* Direct prompt injection  
* Indirect prompt injection  
* System-prompt override  
* Instruction hierarchy weaknesses  
* Jailbreak-style attacks  
* User-controlled content mixed with trusted instructions  
* External content inserted into prompts  
* Retrieved documents containing malicious instructions  
* Cross-user prompt/context contamination

Determine whether prompt injection can actually cross a security boundary rather than merely causing an undesirable model response.  
**Sensitive Information Disclosure**  
Test whether untrusted input can cause the AI or surrounding application to disclose:

* System prompts  
* Secrets  
* API keys  
* Environment variables  
* Database credentials  
* Internal application logic  
* Database schemas  
* Other users' data  
* Other tenants' data  
* Retrieved private documents  
* Tool results  
* Internal instructions

Distinguish model-generated speculation from actual disclosure of sensitive application data.  
**AI Output Handling**  
Trace AI-generated output into application sinks.  
Check whether model output can reach:

* HTML  
* JavaScript  
* SQL  
* Shell commands  
* Templates  
* Markdown renderers  
* File operations  
* API requests  
* Database operations  
* Tool/function arguments

Look specifically for AI-assisted XSS, injection, SSRF, command execution, authorization bypass, or unsafe deserialization.  
**Tool and Function Calling**  
If the model can invoke tools, analyze:

* Available tools  
* Tool authorization  
* User vs system privileges  
* Tool argument validation  
* SQL/database tools  
* File-system tools  
* HTTP/API tools  
* Email/messaging tools  
* Administrative functions  
* External service calls

Determine whether prompt injection can cause unauthorized actions, access to another user's resources, SSRF, data exfiltration, privilege escalation, or destructive operations.  
**AI Resource Exhaustion**  
Analyze:

* Input token limits  
* Output token limits  
* Request limits  
* Per-user quotas  
* Rate limiting  
* Expensive model selection  
* Recursive processing  
* Large-context abuse  
* Repeated AI requests  
* Streaming/resource consumption  
* Cost amplification

Only report DoS or financial-abuse risks when the repository provides a plausible path to meaningful resource exhaustion or cost impact.  
**AI-Generated Content Abuse**  
If the AI provides functionality such as code generation, automated actions, messaging, or content generation, determine whether attackers can abuse it to bypass application controls or cause security-impacting actions.  
Focus on **application security consequences**, not merely the fact that an LLM can produce harmful content.  
**13\. Exploitability Validation**

Before reporting any finding, explicitly verify as many of the following as repository evidence allows:

1. The vulnerable code is reachable.  
2. Attacker-controlled input reaches the relevant sink.  
3. Required privileges are realistically obtainable.  
4. Validation/sanitization is absent or ineffective.  
5. Framework protections do not mitigate the issue.  
6. Middleware does not block exploitation.  
7. Reverse-proxy behavior does not eliminate the attack.  
8. Configuration does not eliminate the risk.  
9. Deployment assumptions are plausible.  
10. There is a realistic exploit path.  
11. The resulting impact is security-relevant.  
12. Existing compensating controls have been considered.

If any critical part cannot be established, downgrade the confidence appropriately and identify the exact manual/runtime verification required.  
**14\. Severity and Confidence**

Assign severity based on actual impact and exploitability, not merely vulnerability category.  
Consider:

* Attacker privileges required  
* Attack complexity  
* User interaction  
* Network accessibility  
* Confidentiality impact  
* Integrity impact  
* Availability impact  
* Scope/cross-tenant impact  
* Exploit reliability  
* Existing mitigations

Use:

* **Critical**  
* **High**  
* **Medium**  
* **Low**  
* **Informational** — only when genuinely security-relevant

Confidence must be one of:

* **Confirmed** — repository evidence establishes the vulnerable flow and realistic exploitability.  
* **Probable** — strong evidence exists, but one or more environmental/runtime assumptions remain.  
* **Needs Manual Verification** — the repository indicates a plausible issue, but exploitation cannot responsibly be established from available evidence.

Do not label theoretical possibilities as confirmed vulnerabilities.  

Calibrate severity with these anchors:

* **Critical**: an unauthenticated actor gains code execution, full data-store access, or takeover of arbitrary accounts or tenants.  
* **High**: an explicit security control is fully defeated with real consequences, such as auth bypass, cross-tenant read or write, stored XSS affecting other users, or authenticated RCE.  
* **Medium**: a real boundary violation with limited blast radius, uncommon preconditions, or a narrow affected resource set.  
* **Low**: disclosure of non-secret internals, or an effect that takes sustained effort for minimal gain.

High vs. Medium: does the issue fully defeat a control for an action with real consequences, or only weaken it? If you cannot state the concrete damage, the severity is lower than it feels. Every finding must name the lower-trust principal, the input they control, the control that should stop it, the boundary crossed, and the concrete result.
**15\. Evidence Requirements**

For every reported vulnerability, provide:

* **Title**  
* **Severity**  
* **Confidence**  
* **CWE**  
* **Affected file(s)**  
* **Affected function/class/route**  
* **Vulnerable code snippet**  
* **Complete source → sink/data flow**  
* **Attacker-controlled input**  
* **Required privileges**  
* **Existing mitigations considered**  
* **Why those mitigations do or do not prevent exploitation**  
* **Realistic exploitation scenario**  
* **Proof of exploitability or precise PoC where appropriate**  
* **Impact**  
* **Exact remediation**  
* **False-positive validation**  
* **Deployment/environment assumptions**  
* **Additional runtime testing required**, if applicable

When possible, reference exact lines or sufficiently precise code locations.  
Do not fabricate line numbers, functions, configuration, runtime behavior, or exploit results.  
**16\. False-Positive Control**

For every finding, actively attempt to disprove it before reporting it.  
Ask:

* Is the code reachable?  
* Is the input actually attacker-controlled?  
* Is the vulnerable branch reachable under realistic conditions?  
* Is authentication required?  
* Is authorization enforced elsewhere?  
* Is there validation before the sink?  
* Is there encoding or sanitization?  
* Is the framework already protecting the operation?  
* Is the middleware applied to this route?  
* Does a reverse proxy block the request?  
* Does deployment configuration change the behavior?  
* Is the suspicious value actually trusted/static?  
* Does exploitation produce meaningful security impact?

If the issue fails these checks, do not report it as a vulnerability.  
**17\. Output Format**

Start with a concise **Executive Summary** describing the overall security posture and the most important findings.  
Then organize findings by:

1. **Critical**  
2. **High**  
3. **Medium**  
4. **Low**  
5. **Informational** — only if security-relevant

For each finding use this structure:  
**\[Severity\] Finding Title**  
**Confidence:** Confirmed / Probable / Needs Manual Verification  
 **CWE:** CWE-XXX  
 **Location:** path/to/file.ext:line  
 **Function:** functionName()  
**Description**  
 Explain the vulnerability and why it matters.  
**Evidence / Vulnerable Code**  
relevant code  
**Source → Sink Flow**  
 Trace attacker-controlled data from its origin through relevant transformations and security controls to the vulnerable sink.  
**Exploitability**  
 Explain the required privileges, conditions, attack path, and realistic exploitation scenario.  
**Existing Protections Considered**  
 List relevant validation, sanitization, framework protections, middleware, proxy behavior, configuration, and deployment controls.  
**Why They Do / Do Not Prevent Exploitation**  
 Explain precisely why the vulnerability remains exploitable, or identify the control that prevents exploitation.  
**Impact**  
 Describe concrete confidentiality, integrity, availability, authorization, financial, tenant-isolation, or other security consequences.  
**Proof of Concept / Validation**  
 Provide a safe, precise reproduction method when the evidence supports it. Do not claim a PoC was executed unless it was actually executed.  
**Remediation**  
 Provide the exact practical fix, including affected code/configuration where possible.  
**False-Positive Validation**  
 Explain why this is not merely a theoretical or already-mitigated issue.  
**Additional Verification**  
 If repository evidence is insufficient, state exactly what runtime test, configuration, or deployment information is required.  
**18\. Final Summary**

End with:  
**Confirmed Vulnerabilities**  
Summarize only findings whose exploitability is sufficiently established.  
**Probable Vulnerabilities**  
Summarize findings with strong evidence but remaining environmental/runtime assumptions.  
**Requires Manual or Runtime Verification**  
List findings that cannot be conclusively established from the repository and specify exactly what must be tested.  
**Security Controls Observed**  
Summarize meaningful controls that are correctly implemented, such as:

* Authentication  
* Authorization  
* CSRF protection  
* Input validation  
* Parameterized queries  
* Output encoding  
* Secure cookies  
* Security headers  
* Rate limiting  
* Secret management  
* Container hardening  
* CI/CD protections  
* AI/tool authorization controls

**Areas Not Fully Verifiable**  
Identify repository areas where security could not be conclusively assessed, such as:

* Production infrastructure  
* Runtime secrets  
* External services  
* Cloud IAM  
* Reverse-proxy behavior  
* WAF configuration  
* Network segmentation  
* Runtime-only feature flags  
* External LLM/API behavior  
* Production database configuration

**Overall Assessment**  
Provide a concise overall assessment based strictly on the evidence found.  
**Important:** Do not manufacture vulnerabilities to make the report look comprehensive. A smaller number of well-proven vulnerabilities is preferable to a large number of speculative findings. Prioritize real exploitability, accurate severity, complete evidence, and actionable remediation.  
