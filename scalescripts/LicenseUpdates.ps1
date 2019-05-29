# Assign licenses to esx servers and VC
Add-PSSnapin vmware.vimautomation.core

    connect-viserver -server esx-mgmt.corp.local -User root -Password VMware1!
    Set-VMHost -VMHost esx-mgmt.corp.local -LicenseKey NH684-VY5D6-W8X8T-0V3HM-1WYM0 -State Connected
    Start-VM -VM vcsa-02a  -Confirm:$false -RunAsync

    connect-viserver -server esx-mgmt-2.corp.local -User root -Password VMware1!
    Set-VMHost -VMHost esx-mgmt-2.corp.local -LicenseKey NH684-VY5D6-W8X8T-0V3HM-1WYM0 -State Connected

    Sleep (600)
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!

function Get-vLicense{
<#
.SYNOPSIS
Function to show all licenses  in vCenter
 
.DESCRIPTION
Use this function to get all licenses in vcenter

#>
	param (
		[Parameter(ValueFromPipeline=$True, HelpMessage="Enter the license key or object")]$LicenseKey = $null,
		[Switch]$showUnused,
		[Switch]$showEval
		)
	$servInst = Get-View ServiceInstance
	$licenceMgr = Get-View $servInst.Content.licenseManager
	if ($showUnused -and $showEval){
		$licenses = $licenceMgr.Licenses | where {$_.EditionKey -eq "eval" -or $_.Used -eq 0}
	}elseif($showUnused){
		$licenses = $licenceMgr.Licenses | where {$_.EditionKey -ne "eval" -and $_.Used -eq 0}
	}elseif($showEval){
		$licenses = $licenceMgr.Licenses | where {$_.EditionKey -eq "eval"}
	}elseif ($LicenseKey -ne $null) {
		if (($LicenseKey.GetType()).Name -eq "String"){
			$licenses = $licenceMgr.Licenses | where {$_.LicenseKey -eq $LicenseKey}
		}else {
			$licenses = $licenceMgr.Licenses | where {$_.LicenseKey -eq $LicenseKey.LicenseKey}
		}
	}
	else {
		$licenses = $licenceMgr.Licenses | where {$_.EditionKey -ne "eval"}
	}
	
	$licenses
}

function Add-vLicense{
<#
.SYNOPSIS
Add New Licenses to the vCenter license manager
 
.DESCRIPTION
Use this function to add licenses  and assing to either the vcenter or the hosts

#>

param (
	$VMHost ,
	[Parameter(ValueFromPipeline=$True)]$License = $null,
	[string]$LicenseKey = "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
	[switch]$AddKey
    )
	$LicenseMgr = Get-View -Id 'LicenseManager-LicenseManager'

	$LicenseAssignMgr = Get-View -Id 'LicenseAssignmentManager-LicenseAssignmentManager'
	if($License){
		$LicenseKey = $License.LicenseKey
		$LicenseType = $LicenseMgr.DecodeLicense($LicenseKey)
	}else{
		$LicenseType = $LicenseMgr.DecodeLicense($LicenseKey)
	}
	
	if ($LicenseType) {
		if ($AddKey){
			$LicenseMgr.AddLicense($LicenseKey, $null)
		}else{
			if ($LicenseType.EditionKey -match "vc"){
				#$servInst = Get-View ServiceInstance
				$Uuid = (Get-View ServiceInstance)[0].Content.About.InstanceUuid
				$LicenseAssignMgr.UpdateAssignedLicense($Uuid,$LicenseKey,$null)                           
			} else {
				$key = Get-vLicense -LicenseKey $LicenseKey
				if($key  -and ($key.Total-$key.Used) -lt (get-vmhost $VMHost | get-view).Hardware.CpuInfo.NumCpuPackages){
					Write-Host "Not Enough licenses left"
				} else{
					$Uuid = (Get-VMhost $VMHost | Get-View).MoRef.Value
					$licenseAssignMgr.UpdateAssignedLicense($Uuid, $LicenseKey,$null)
				}
			}	
		}
	}	
}


function Remove-vLicense{
<#
.SYNOPSIS
Function to remove a licenses that is not in use in vCenter
 
.DESCRIPTION
Use this function to remove a license
 
#>
param (
	[Parameter(Position=0, Mandatory=$true, ValueFromPipeline=$True, HelpMessage="Enter the key or keyobject to remove")]$License
	)
	$LicObj = Get-vLicense $License 
	if($LicObj.Used -eq 0){
		$LicenseMgr = Get-View -Id 'LicenseManager-LicenseManager'
		$LicenseMgr.RemoveLicense($LicObj.LicenseKey)
	}else{
		Write-Host " The license is assigned and cannot be removed"
	}
}

#Adding a new License Key
Add-vLicense -LicenseKey J4006-QC28K-D8W93-0V0K2-C0P04 -AddKey
#Assign the license to vCenter
Get-vLicense -LicenseKey J4006-QC28K-D8W93-0V0K2-C0P04 | Add-vLicense
Sleep(60)

# code to reconnect the hosts to the vCenter
$Hosts = Get-VMHost | where { $_.ConnectionState -eq "Disconnected" }
foreach ($esx in $Hosts) {
  Set-VMHost -VMHost $esx -State Connected
}