param($index)
. ".\HttpRest.ps1" 
Add-PSSnapin vmware.vimautomation.core
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!

$cluster = "ScaleCluster"+$index




#$headers = @{Authorization = $basicAuthValue;Accept='application/xml'}


<#-----FUNCTION TO GET DISK RESOURCE FROM FREENAS SERVER-----#>
Function getHostPreparationStatus([string] $clusterID)
{
    $hostPrepStatusflag = $false
    $firewallStatusflag = $false
    $getNetworkFabricStatusURI = "/api/2.0/nwfabric/status?resource="+$clusterId
    Write-host "Host Preparation Status URI is $getNetworkFabricStatusURI"
    $test = http-rest-xml "GET" $getNetworkFabricStatusURI
    $resourseStatus = $test.resourceStatuses.resourceStatus
    Foreach ($nwFabricFeatureStatus in $resourseStatus.nwFabricFeatureStatus) 
    {
        $featureId = $nwFabricFeatureStatus.featureId
        if( $featureId -eq "com.vmware.vshield.vsm.nwfabric.hostPrep")
        {
            $status = $nwFabricFeatureStatus.status
            write-host "Host Preparation status is $status" 
            if( $status -eq "GREEN" )
            {
                
                $hostPrepStatusflag = $true
            }
        }
        if( $featureId -eq "com.vmware.vshield.firewall")
        {
            $status = $nwFabricFeatureStatus.status
            write-host "Firewall status is $status"  
            if( $status -eq "GREEN" )
            {
                
                $firewallStatusflag = $true
            }
        }
    }
    
    if( $hostPrepStatusflag -eq $true -and  $firewallStatusflag -eq $true )
    {
      return $true
    }
    else {
      return $false
    }
   
}


<#-----STEPS FOR CHECKING NSX HOST PREPARATION AND FIREWALL STATUS-----#>


try
{
    $clusterobj = Get-Cluster -Name $cluster
    #$clusterId = $clusterobj.Id.TrimStart("ClusterComputeResource-")
    $clusterId = $clusterobj.ExtensionData.MoRef.Value
    write-Host "Checking NSX Host Preparation and Firewall status in Cluster "$clusterobj.Name
    write-Host "Cluster Id for $cluster is "$clusterobj.Id
    
    do {

        $return = getHostPreparationStatus $clusterId
        if( $return -eq $false)
        {
            Write-host " NSX Host Preparation or Firewall status is not UP in cluster $cluster, polling ..." -ForegroundColor Yellow
            sleep 5
        }
        else
        {
            Write-host " NSX Host Preparation and Firewall status is UP in cluster $cluster" -ForegroundColor Green
        }
    } while ($return -eq $false )
}
catch
{
    Write-Error "Exception in retrieving NSX Host preparation or Firewall Status in cluster $cluster"
    return $false
}
    
Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false

