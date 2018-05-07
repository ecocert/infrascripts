param($index,$servicename)
(Get-Location).Path+"\HttpRest.ps1"
Add-PSSnapin vmware.vimautomation.core
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!

#$index=1
$cluster = "ScaleCluster"+$index
$dataStore= "SVM-DataStore-$index"
$dvportgroup = "vDS_VM_pg"
$ippoolname = "SVM_IP_POOL"+$index

<#-----FUNCTION TO DEPLOY SERVICE-----#>
Function deployService([string] $clusterID, [string] $datastoreID, [string] $serviceID, [string] $dvportgroupID, [string] $ippoolID)
{


    try
    {

        
        $body ="<clusterDeploymentConfigs>
                <clusterDeploymentConfig>
                <clusterId>$clusterID</clusterId>
                <datastore>$datastoreID</datastore>
                <services>
                <serviceDeploymentConfig>
                <serviceId>$serviceID</serviceId>
                <dvPortGroup>$dvportgroupID</dvPortGroup>
                <ipPool>$ippoolID</ipPool>
                </serviceDeploymentConfig>
                </services>
                </clusterDeploymentConfig>
                </clusterDeploymentConfigs>"

        $serviceDeploymentURI = "/api/2.0/si/deploy"
        write-debug "service deployment body is $body"
        $test = http-rest-xml "POST" $serviceDeploymentURI $body

        write-host "Response for service deployment is $test"
        return $true
      
    }
    catch 
    {
        write-warning "Exception in deploying service"
        throw $_
        return $false 
    } 

}




<#-----STEPS FOR SVM DEPLOYMENT-----#>


try
{

    "## Fetching NSX Cluster $cluster MoRef ..."
    $cluster_obj = Get-Cluster $cluster
    
    $cluster_moref = $cluster_obj.ExtensionData.MoRef.Value
    "-> cluster ID : $cluster_moref"
        

    "## Fetching NSX Cluster Datastore $datastore MoRef ..."
    $datastore_obj = $cluster_obj | Get-Datastore $datastore
    
    $datastore_moref = $datastore_obj.ExtensionData.MoRef.Value
    "-> DataStore ID : $datastore_moref"
    

    "## Fetching NSX Management dvPortgroup $dvportgroup MoRef ..."
    $dvportgroup_obj = Get-VirtualSwitch -Name "vDS_data" | Get-VirtualPortGroup -Name $dvportgroup
    $portgroup_moref = $dvportgroup_obj.ExtensionData.MoRef.Value
    "-> dvPortgroup ID : $portgroup_moref"

    "# Fetching Service ID for $servicename ..."

    $services = http-rest-json "GET" "/api/2.0/si/services"
    $services_json = $services | ConvertFrom-Json

    $serviceFound = $false
    Foreach ($service in $services_json.services) {
      if ($service.name -eq $servicename) {
        $serviceID = $service.objectId
        $serviceFound = $true
      }
     
    }
    if( $serviceFound -eq $false )
    {
        write-error "service ID not found for $servicename"
        return $false
    }
    "-> NSX $servicename ID  : $serviceID"


    "# Fetching NSX IP Pool ID for $ippoolname ..."


    $pools = http-rest-json "GET" "/api/2.0/services/ipam/pools/scope/globalroot-0"
    $pools_json = $pools | ConvertFrom-Json

    $ippoolFound = $false
    Foreach ($ippool in $pools_json.ipAddressPools) {
        if ($ippool.name -eq $ippoolname) {
            $ippoolid = $ippool.objectId
            $ippoolFound = $true
        }
  
    }
     if( $ippoolFound -eq $false )
    {
        write-error "IP pool ID not found for $ippoolname"
        return $false
    }
    "-> NSX $ippoolname ID  : $ippoolid"
    
    $return = deployService $cluster_moref $datastore_moref $serviceID $portgroup_moref $ippoolid
    if( $return -eq $false)
    {
        Write-Error " Unable to deploy $servicename in Cluster $cluster"
        return $false
    }
}
catch
{
    Write-Error "Exception in deploying service in cluster $cluster"
    return $false
}
    
Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false
