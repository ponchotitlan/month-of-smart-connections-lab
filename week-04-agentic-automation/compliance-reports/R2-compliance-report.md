# Cisco IOS-XE Hardening Compliance Report - R2

**Device**: R2  
**IP Address**: 10.10.20.172  
**Platform**: Cisco IOS-XE (IOL)  
**Report Date**: 2026-02-25  
**Compliance Standard**: Cisco IOS-XE Security Hardening Guide  
**Reference**: https://sec.cloudapps.cisco.com/security/center/resources/IOS_XE_hardening

---

## Executive Summary

This compliance report evaluates device **R2** against the Cisco IOS-XE Security Hardening best practices. The assessment reveals significant security gaps requiring immediate remediation.

### Overall Compliance Score: **15% (3/20)**

**Risk Level**: 🔴 **HIGH**

---

## Compliance Summary Table

| # | Security Control | Status | Finding |
|---|-----------------|--------|---------|
| 1 | **Enable Secret Password** | ❌ **FAIL** | Using `enable password` (weak) instead of `enable secret` (encrypted) |
| 2 | **Strong Passwords** | ❌ **FAIL** | Weak passwords detected ("cisco") - not meeting complexity requirements |
| 3 | **AAA Authentication** | ❌ **FAIL** | AAA not configured (`no aaa new-model`) - local authentication only |
| 4 | **Console Timeout** | ❌ **FAIL** | Console timeout set to 0 (never expires) - should be 5-10 minutes |
| 5 | **VTY Timeout** | ❌ **FAIL** | VTY timeout set to 0 (never expires) - should be 5-10 minutes |
| 6 | **VTY Access Control** | ❌ **FAIL** | No ACL applied to VTY lines - unrestricted access |
| 7 | **Login Banner** | ❌ **FAIL** | No login banner configured |
| 8 | **Service Password Encryption** | ❌ **FAIL** | `service password-encryption` not enabled - passwords in clear text |
| 9 | **Disable Unused Services** | ⚠️ **PARTIAL** | HTTP server enabled - should disable if not needed |
| 10 | **SSH Configuration** | ⚠️ **PARTIAL** | SSH enabled but version not enforced to v2 only |
| 11 | **Telnet Access** | ❌ **FAIL** | Telnet enabled on VTY lines - should use SSH only |
| 12 | **Logging** | ⚠️ **PARTIAL** | Console logging disabled, but no external logging configured |
| 13 | **SNMP** | ✅ **PASS** | No SNMP configured |
| 14 | **CDP** | ⚠️ **UNKNOWN** | CDP status not visible in config (may be enabled by default) |
| 15 | **Source Routing** | ⚠️ **UNKNOWN** | Not explicitly disabled |
| 16 | **Proxy ARP** | ⚠️ **UNKNOWN** | Not explicitly disabled on interfaces |
| 17 | **Directed Broadcast** | ✅ **PASS** | Not enabled (disabled by default) |
| 18 | **TCP Keepalives** | ❌ **FAIL** | Not configured for better session management |
| 19 | **Gratuitous ARP** | ⚠️ **UNKNOWN** | Not explicitly configured |
| 20 | **Interface Security** | ⚠️ **PARTIAL** | Unused interface (Eth0/3) is shutdown ✅, but no port-security configured |

---

## Detailed Findings

### 🔴 Critical Security Issues (Priority 1 - Immediate Action Required)

#### 1. Weak Enable Password
**Current Configuration:**
```
enable password cisco
```
**Issue**: Using `enable password` stores the password in a reversible Type 7 encryption which is easily cracked. The password "cisco" is also weak and commonly known.

**Recommendation:**
```
no enable password
enable secret <strong-password>
```

---

#### 2. No AAA Configuration
**Current Configuration:**
```
no aaa new-model
```
**Issue**: Device relies solely on local authentication without centralized AAA services. No accounting or authorization policies enforced.

**Recommendation:**
```
aaa new-model
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+
```

---

#### 3. Telnet Enabled
**Current Configuration:**
```
line vty 0 4
 transport input telnet ssh
```
**Issue**: Telnet transmits all data including credentials in clear text over the network.

**Recommendation:**
```
line vty 0 4
 transport input ssh
```

---

#### 4. Infinite Session Timeouts
**Current Configuration:**
```
line con 0
 exec-timeout 0 0
line vty 0 4
 exec-timeout 0 0
```
**Issue**: Sessions never timeout, allowing abandoned sessions to remain active indefinitely.

**Recommendation:**
```
line con 0
 exec-timeout 5 0
line vty 0 4
 exec-timeout 5 0
```

---

#### 5. No VTY Access Control List
**Current Configuration:**
```
line vty 0 4
 password cisco
 login local
 transport input telnet ssh
```
**Issue**: VTY lines accept connections from any source IP address without restriction.

**Recommendation:**
```
ip access-list standard MANAGEMENT-ACCESS
 permit 10.10.20.0 0.0.0.255
 deny any log

line vty 0 4
 access-class MANAGEMENT-ACCESS in
```

---

#### 6. Weak User Passwords
**Current Configuration:**
```
username cisco password 0 cisco
```
**Issue**: Username and password are both set to "cisco" - a well-known default credential. Type 0 means unencrypted.

**Recommendation:**
```
username admin privilege 15 secret <strong-password>
```

---

### ⚠️ High Security Issues (Priority 2 - Address Within 7 Days)

#### 7. Service Password Encryption Not Enabled
**Issue**: Passwords in configuration are stored in clear text or weak Type 7 encryption.

**Recommendation:**
```
service password-encryption
```

---

#### 8. No Login Banner
**Issue**: Missing legal warning banner that establishes expectation of privacy.

**Recommendation:**
```
banner login ^
******************************************************************
WARNING: Unauthorized access to this system is forbidden and will
be prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.
******************************************************************
^
```

---

#### 9. HTTP Services Enabled
**Current Configuration:**
```
ip http server
ip http secure-server
```
**Issue**: HTTP/HTTPS services are enabled and may not be needed, increasing attack surface.

**Recommendation:** If not required:
```
no ip http server
no ip http secure-server
```

---

#### 10. SSH Not Enforced to Version 2
**Current Configuration:**
```
ip ssh bulk-mode 131072
ip ssh server algorithm authentication password
```
**Issue**: SSH version not explicitly set to v2 only. SSHv1 has known vulnerabilities.

**Recommendation:**
```
ip ssh version 2
ip ssh server algorithm encryption aes128-ctr aes192-ctr aes256-ctr
ip ssh server algorithm mac hmac-sha2-256 hmac-sha2-512
```

---

### ℹ️ Medium Security Issues (Priority 3 - Address Within 30 Days)

#### 11. No Remote Logging Configured
**Current Configuration:**
```
no logging console
```
**Issue**: Console logging is disabled, but no remote syslog server is configured for audit trails.

**Recommendation:**
```
logging host <syslog-server-ip>
logging trap informational
logging source-interface <interface>
service timestamps log datetime msec localtime show-timezone
```

---

#### 12. TCP Keepalives Not Configured
**Issue**: TCP keepalives help detect and clear hung sessions.

**Recommendation:**
```
service tcp-keepalives-in
service tcp-keepalives-out
```

---

#### 13. CDP Status Unknown
**Issue**: Cisco Discovery Protocol may be enabled by default, potentially leaking information to unauthorized devices.

**Recommendation:**
```
no cdp run
! Or disable per-interface:
interface range Ethernet0/0 - 3
 no cdp enable
```

---

#### 14. IP Source Routing Not Disabled
**Issue**: IP source routing should be explicitly disabled to prevent routing manipulation attacks.

**Recommendation:**
```
no ip source-route
```

---

#### 15. Gratuitous ARP Not Configured
**Issue**: Should enable gratuitous ARP updates for faster convergence and security.

**Recommendation:**
```
ip arp gratuitous
```

---

#### 16. No Interface Port Security
**Issue**: Access interfaces do not have port-security configured to limit MAC addresses.

**Recommendation:** For access ports:
```
interface Ethernet0/0
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security aging time 10
```

---

## ✅ Compliant Items

The following controls are properly configured:

1. **SNMP**: No SNMP configured (reducing attack surface) ✅
2. **Directed Broadcast**: Not enabled (disabled by default in IOS-XE) ✅
3. **Unused Interfaces**: Ethernet0/3 is properly shutdown ✅

---

## Remediation Priority

### Immediate (Next 24 Hours)
1. Change all default passwords
2. Configure `enable secret` with strong password
3. Disable Telnet, enforce SSH v2 only
4. Apply VTY access-class with management ACL
5. Set reasonable exec timeouts

### Short Term (Next 7 Days)
6. Enable AAA with TACACS+ or RADIUS
7. Enable service password-encryption
8. Configure login banner
9. Disable HTTP/HTTPS if not needed
10. Configure remote logging

### Medium Term (Next 30 Days)
11. Implement port-security on access interfaces
12. Disable CDP if not required
13. Configure TCP keepalives
14. Disable IP source routing
15. Review and harden interface configurations

---

## Risk Assessment

| Risk Category | Count | Percentage |
|--------------|-------|------------|
| 🔴 Critical (FAIL) | 11 | 55% |
| ⚠️ High/Medium (PARTIAL/UNKNOWN) | 6 | 30% |
| ✅ Compliant (PASS) | 3 | 15% |

**Overall Risk Level**: 🔴 **HIGH** - Immediate remediation required

---

## Conclusion

Device R2 has significant security vulnerabilities that require immediate attention. The most critical issues include:

- Use of weak default credentials
- Lack of AAA authentication
- Telnet access enabled
- No session timeouts
- No VTY access controls

These vulnerabilities expose the device to unauthorized access, credential compromise, and potential network breaches.

**Recommended Next Steps:**
1. Review and approve proposed remediation configurations
2. Schedule maintenance window for configuration changes
3. Implement critical fixes first (Priority 1)
4. Retest compliance after remediation
5. Implement continuous compliance monitoring

---

**Report Generated By**: Network Automation Assistant  
**Analysis Date**: 2026-02-25  
**Configuration Analyzed**: R2 running-config (3631 bytes)  
**Next Review Date**: 2026-03-25 (30 days)
