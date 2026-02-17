*** Settings ***
Documentation     Month of Smart Connections Lab - Week 3: Trust Issues
...               Network Device Interface Audit using gNMI
...               This test suite verifies interface names, descriptions, and statuses
...               using OpenConfig models via gNMI protocol

Library           GnmiLibrary.py
Library           Collections
Library           BuiltIn

Suite Setup       Setup Test Environment
Suite Teardown    Cleanup Test Environment

*** Variables ***
# Device connection parameters (override from command line)
${DEVICE_NAME}        router1
${DEVICE_HOST}        192.168.1.10
${DEVICE_PORT}        57400
${DEVICE_USERNAME}    admin
${DEVICE_PASSWORD}    admin123
${DEVICE_INSECURE}    ${True}

# Expected interfaces file
${EXPECTED_FILE}      expected_interfaces.json

*** Test Cases ***
Explore Interfaces
    [Documentation]    Retrieve and display all interface configurations
    [Tags]    troubleshoot    explore
    
    ${interfaces_json}=    Get Interfaces Via GNMI    ${DEVICE_NAME}
    @{interfaces}=    Parse Interfaces From JSON    ${interfaces_json}
    
    Log    Found ${SPACE}${interfaces.__len__()}${SPACE}interfaces
    FOR    ${interface}    IN    @{interfaces}
        Log    🔌 Interface: ${interface}[name] - ${interface}[description] - Admin: ${interface}[admin_status], Oper: ${interface}[oper_status]
    END

Audit Interface Configuration On Device
    [Documentation]    Connect to device and verify interface presence, descriptions, and statuses
    [Tags]    interface    audit    multivendor
    
    Audit Device Interfaces

*** Keywords ***
Setup Test Environment
    [Documentation]    Initialize connection parameters and prepare for testing
    Connect To Device Inline    ${DEVICE_NAME}    ${DEVICE_HOST}    ${DEVICE_PORT}
    ...    ${DEVICE_USERNAME}    ${DEVICE_PASSWORD}    ${DEVICE_INSECURE}
    Log    🔗 Device ${DEVICE_NAME} successfully connected via gNMI to port ${DEVICE_PORT}

Cleanup Test Environment
    [Documentation]    Disconnect from device and cleanup
    Disconnect All
    Disconnect From Device    ${DEVICE_NAME}
    Log    🧹 Test environment cleaned up

Audit Device Interfaces
    [Documentation]    Connect to device and verify interfaces match expected configuration
    
    # Get actual interfaces from device
    ${actual_interfaces_json}=    Get Interfaces Via GNMI    ${DEVICE_NAME}
    @{actual_interfaces}=    Parse Interfaces From JSON    ${actual_interfaces_json}
    
    # Load expected interfaces
    @{expected_interfaces}=    Load Expected Interfaces    ${EXPECTED_FILE}    ${DEVICE_NAME}
    
    # Verify each expected interface
    FOR    ${expected}    IN    @{expected_interfaces}
        ${actual}=    Verify Interface Exists    ${expected}[name]    ${actual_interfaces}
        Should Not Be Equal    ${actual}    ${None}
        ...    msg=Interface ${expected}[name] not found on ${DEVICE_NAME}
        
        # Verify description if specified
        Run Keyword If    '${expected}[description]' != ''
        ...    Should Be Equal    ${actual}[description]    ${expected}[description]
        ...    msg=Interface ${expected}[name] description mismatch. Expected: ${expected}[description], Got: ${actual}[description]
        
        # Verify admin status if specified
        Run Keyword If    '${expected}[admin_status]' != ''
        ...    Should Be Equal    ${actual}[admin_status]    ${expected}[admin_status]
        ...    msg=Interface ${expected}[name] admin status mismatch. Expected: ${expected}[admin_status], Got: ${actual}[admin_status]
        
        # Verify operational status if specified
        Run Keyword If    '${expected}[oper_status]' != ''
        ...    Should Be Equal    ${actual}[oper_status]    ${expected}[oper_status]
        ...    msg=Interface ${expected}[name] operational status mismatch. Expected: ${expected}[oper_status], Got: ${actual}[oper_status]
    END
