#
# NSX-Callback-Scale-Config-Services
# Description: Get IpAddress of all Guest VMs with Prefix
#
# Author: Satya Dillikar <sdillikar@vmware.com>
# Version: 1.0
# Date: 08/FEB/2018
#

Import-module VMware.VimAutomation.Core

#$VcenterIpAddess = "192.168.110.90"
$VcenterIpAddess = "172.17.11.10"
$Username = "administrator@corp.local"
$Password = "VMware1!"
$CWD = "F:\scriptRepo\infrascripts\testall\CallbackScale362"
$GVMFilename = $CWD + "\input\gvm_object_ids.txt"
$LogFilename = $CWD + "\output\ps_gvm_objects.log"
$VMPrefix = "Linux-VM*"
#$VMPrefix = "Trend*"

$SecPassword = $Password | ConvertTo-SecureString -AsPlainText -Force
$Credential = New-Object -TypeName pscredential -ArgumentList $Username,$SecPassword

$EServer = Connect-VIServer $VcenterIpAddess -Protocol https -Credential $Credential

Remove-item $GVMFilename -ErrorAction SilentlyContinue
Remove-item $LogFilename -ErrorAction SilentlyContinue

$allVMs = Get-VM -name $VMPrefix
 ForEach ($VM in $allVMs) {  
    #Write-Host $VM.extensiondata.Moref.Value
    Out-File -FilePath $GVMFilename -InputObject $VM.extensiondata.Moref.Value -Encoding ASCII -Append
 } 
Get-VM -name $VMPrefix| Select Name, @{N="ID";E={@($_.extensiondata.Moref.Value)}} | Set-Content -Encoding ASCII $LogFilename
Disconnect-VIServer -Server $EServer -Confirm:$false
