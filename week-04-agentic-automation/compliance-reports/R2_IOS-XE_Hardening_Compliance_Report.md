# R2 IOS-XE Hardening Compliance Report

**Generated:** 2024-02-26  
**Device:** R2  
**Platform:** IOS-XE (IOL)  
**Reference:** [Cisco IOS-XE Hardening Guide](https://sec.cloudapps.cisco.com/security/center/resources/IOS_XE_hardening)

---

## Executive Summary

This report evaluates device **R2** against Cisco IOS-XE hardening best practices. The assessment covers authentication, session management, secure protocols, logging, and control plane security.

### Overall Compliance Score: **24% (5/21 checks passed)**

**Critical Findings:**
- ❌ AAA authentication disabled
- ❌ Plaintext passwords in use
- ❌ No session timeouts configured
- ❌ Insecure protocols enabled (Telnet, HTTP)
- ❌ No control plane protection

---

## Detailed Compliance Matrix

| # | Category | Item | Status | Finding | Remediation Priority |
|---|----------|------|--------|---------|---------------------|
| 1 | Authentication & Authorization | AAA Configuration | ❌ **FAIL** | `no aaa new-model` - AAA is disabled | **CRITICAL** |
| 2 | Authentication & Authorization | Enable Secret | ❌ **FAIL** | Using `enable password cisco` (plaintext) instead of `enable secret` | **CRITICAL** |
| 3 | Authentication & Authorization | Strong Passwords | ❌ **FAIL** | Weak password "cisco" used throughout | **CRITICAL** |
| 4 | Authentication & Authorization | Local User Passwords | ❌ **FAIL** | `username cisco password 0 cisco` - plaintext password | **CRITICAL** |
| 5 | Authentication & Authorization | Login Banner | ❌ **FAIL** | No login banner configured | **MEDIUM** |
| 6 | Session Management | Console Timeout | ❌ **FAIL** | `exec-timeout 0 0` on console - No timeout | **HIGH** |
| 7 | Session Management | VTY Timeout | ❌ **FAIL** | `exec-timeout 0 0` on VTY lines - No timeout | **HIGH** |
| 8 | Session Management | VTY ACLs | ❌ **FAIL** | No access-class ACL restricting VTY access | **HIGH** |
| 9 | Secure Management | SSH Version 2 | ⚠️ **PARTIAL** | SSH enabled but version not enforced to v2 only | **MEDIUM** |
| 10 | Secure Management | Telnet Disabled | ❌ **FAIL** | `transport input telnet ssh` - Telnet protocol enabled | **CRITICAL** |
| 11 | Secure Management | HTTP Server | ❌ **FAIL** | `ip http server` enabled (unencrypted) | **HIGH** |
| 12 | Secure Management | HTTPS Server | ✅ **PASS** | `ip http secure-server` enabled | N/A |
| 13 | Logging & Monitoring | Timestamps | ✅ **PASS** | `service timestamps log datetime msec` configured | N/A |
| 14 | Logging & Monitoring | Login Success Logging | ✅ **PASS** | `login on-success log` enabled | N/A |
| 15 | Logging & Monitoring | Centralized Logging | ❌ **FAIL** | No `logging host` configured | **MEDIUM** |
| 16 | Logging & Monitoring | Console Logging | ⚠️ **INFO** | `no logging console` - console logging disabled | **LOW** |
| 17 | Services Hardening | CDP | ⚠️ **INFO** | CDP not explicitly disabled globally or on external interfaces | **LOW** |
| 18 | Services Hardening | NTP | ❌ **FAIL** | No NTP server configured for time synchronization | **MEDIUM** |
| 19 | Services Hardening | SNMP v3 | ❌ **FAIL** | No SNMP configuration; if needed, use SNMPv3 | **MEDIUM** |
| 20 | Control Plane | Control Plane Policing | ❌ **FAIL** | No CoPP (Control Plane Policing) configured | **HIGH** |
| 21 | Control Plane | Control Plane Protection | ❌ **FAIL** | No CPPr (Control Plane Protection) configured | **HIGH** |
| 22 | Network Security | Infrastructure ACLs | ❌ **FAIL** | No infrastructure protection ACLs configured | **HIGH** |
| 23 | Network Security | Unicast RPF | ❌ **FAIL** | No uRPF configured on interfaces | **MEDIUM** |
| 24 | Cryptography | Domain Name | ✅ **PASS** | `ip domain name virl.info` configured | N/A |
| 25 | Cryptography | PKI Certificate | ✅ **PASS** | Self-signed certificate present for secure services | N/A |

---

## Critical Vulnerabilities

### 🔴 1. Weak Authentication (CRITICAL)

**Issue:** Device uses plaintext passwords and AAA is disabled.

**Current Configuration:**
```
no aaa new-model
enable password cisco
username cisco password 0 cisco
```

**Risk:** Passwords easily compromised; no centralized authentication; credentials visible in configuration.

**Recommendation:**
```
aaa new-model
aaa authentication login default local
aaa authorization exec default local
enable secret <strong-password>
username admin privilege 15 secret <strong-password>
```

---

### 🔴 2. Insecure Management Protocols (CRITICAL)

**Issue:** Telnet and unencrypted HTTP are enabled.

**Current Configuration:**
```
ip http server
line vty 0 4
 transport input telnet ssh
```

**Risk:** Credentials and data transmitted in cleartext; susceptible to man-in-the-middle attacks.

**Recommendation:**
```
no ip http server
line vty 0 4
 transport input ssh
ip ssh version 2
```

---

### 🔴 3. No Session Timeouts (HIGH)

**Issue:** Console and VTY sessions never timeout.

**Current Configuration:**
```
line con 0
 exec-timeout 0 0
line vty 0 4
 exec-timeout 0 0
```

**Risk:** Unattended sessions remain active indefinitely; unauthorized access possible.

**Recommendation:**
```
line con 0
 exec-timeout 5 0
line vty 0 4
 exec-timeout 10 0
```

---

### 🟡 4. No VTY Access Control (HIGH)

**Issue:** No ACL restricting management access.

**Current Configuration:**
```
line vty 0 4
 password cisco
 login local
 transport input telnet ssh
```

**Risk:** Any IP address can attempt to connect to VTY lines.

**Recommendation:**
```
ip access-list standard MGMT-ACL
 permit 10.10.20.0 0.0.0.255
 permit 10.26.5.0 0.0.0.255
 deny any log

line vty 0 4
 access-class MGMT-ACL in
```

---

### 🟡 5. No Control Plane Protection (HIGH)

**Issue:** No CoPP or CPPr configured to protect the control plane.

**Risk:** Device vulnerable to DoS attacks targeting routing protocols and management services.

**Recommendation:**
Implement Control Plane Policing (CoPP) to rate-limit traffic destined to the router's control plane.

---

## Compliance Statistics

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ PASS | 5 | 24% |
| ⚠️ PARTIAL/INFO | 3 | 14% |
| ❌ FAIL | 13 | 62% |

---

## Remediation Roadmap

### Phase 1: Immediate (CRITICAL - Deploy within 24 hours)
1. Disable Telnet: `line vty 0 4` → `transport input ssh`
2. Disable HTTP: `no ip http server`
3. Enable AAA: `aaa new-model`
4. Replace plaintext passwords with encrypted secrets
5. Enforce SSH version 2: `ip ssh version 2`

### Phase 2: Short-term (HIGH - Deploy within 1 week)
1. Configure session timeouts on console and VTY lines
2. Implement VTY access-class ACLs
3. Configure Control Plane Policing (CoPP)
4. Add infrastructure protection ACLs

### Phase 3: Medium-term (MEDIUM - Deploy within 1 month)
1. Configure centralized logging to syslog server
2. Configure NTP for time synchronization
3. Add login banners
4. Implement Unicast RPF on external interfaces
5. Review and disable unnecessary services (CDP on external interfaces)

---

## Configuration Snippet - Quick Wins

```cisco
! Phase 1: Critical Security Hardening
configure terminal

! 1. Enable AAA
aaa new-model
aaa authentication login default local
aaa authorization exec default local

! 2. Strong passwords
enable secret MyStr0ngP@ssw0rd!
username admin privilege 15 secret MyStr0ngAdm1nP@ss!

! 3. Disable insecure protocols
no ip http server
ip ssh version 2

! 4. Secure VTY lines
line vty 0 4
 exec-timeout 10 0
 transport input ssh
 login local

! 5. Secure console
line con 0
 exec-timeout 5 0

! 6. Add login banner
banner login ^C
**************************************************************************
*                                                                        *
*  UNAUTHORIZED ACCESS TO THIS DEVICE IS PROHIBITED                     *
*  You must have explicit, authorized permission to access this device. *
*  All activities performed on this device are logged and monitored.    *
*                                                                        *
**************************************************************************
^C

! 7. VTY Access Control
ip access-list standard MGMT-ACL
 remark Management access only
 permit 10.10.20.0 0.0.0.255
 permit 10.26.5.0 0.0.0.255
 deny any log

line vty 0 4
 access-class MGMT-ACL in

! 8. Configure logging
logging host 10.10.20.10
logging trap informational
logging source-interface Loopback100

! 9. Configure NTP
ntp server 10.10.20.1 prefer
ntp source Loopback100

end
write memory
```

---

## Conclusion

Device **R2** currently exhibits **significant security deficiencies** and is **not compliant** with Cisco IOS-XE hardening best practices. The device is vulnerable to:

- Credential theft (plaintext passwords)
- Man-in-the-middle attacks (Telnet/HTTP enabled)
- Unauthorized access (no session timeouts, no VTY ACLs)
- Control plane attacks (no CoPP/CPPr)

**Immediate action is required** to address critical vulnerabilities, particularly:
1. Disabling insecure protocols (Telnet, HTTP)
2. Implementing encrypted authentication
3. Enforcing session timeouts
4. Restricting management access with ACLs

A phased remediation approach is recommended, prioritizing critical security controls first.

---

**Report Generated by:** Network Automation Assistant  
**Date:** 2024-02-26  
**Next Review:** Recommended within 30 days after remediation