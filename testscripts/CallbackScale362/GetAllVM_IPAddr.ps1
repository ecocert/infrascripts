#
# NSX-Callback-Scale-Config-Services
# Description: Get IpAddress of all Guest VMs with Prefix
#
# Author: Satya Dillikar <sdillikar@vmware.com>
# Version: 1.0
# Date: 08/FEB/2018
#

Import-module VMware.VimAutomation.Core

$VcenterIpAddess = "192.168.110.90"
$Username = "administrator@corp.local"
$Password = "VMware1!"
$GVMFilename = ".\input\gvm_ip_addresses.txt"
$LogFilename = ".\output\ps_gvm_ip_addrs.log"
$VMPrefix = "Linux-VM*"

$SecPassword = $Password | ConvertTo-SecureString -AsPlainText -Force
$Credential = New-Object -TypeName pscredential -ArgumentList $Username,$SecPassword

$EServer = Connect-VIServer $VcenterIpAddess -Protocol https -Credential $Credential

Remove-item $GVMFilename -ErrorAction SilentlyContinue
#first ip addr is IPV4 Get only one ip-addr
Get-VM -name $VMPrefix| Select Name, @{N="IP";E={@($_.guest.IPaddress[0])}} | Set-Content -Encoding ASCII $LogFilename
Get-VM -name $VMPrefix| Select @{N="IP";E={@($_.guest.IPaddress[0])}} | foreach { if ($_.IP) { write-output ($_.IP) }} | Set-Content -Encoding ASCII $GVMFilename

Disconnect-VIServer -Server $EServer -Confirm:$false
