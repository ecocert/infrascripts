param([Int32]$index, $method)
. "F:/scriptRepo/infrascripts/testall/scalescripts/HttpRest.ps1"
Add-PSSnapin vmware.vimautomation.core
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!

$cluster = "ScaleCluster"+$index



<#-----FUNCTION TO DO HOST PREPARATION-----#>
Function InstallNVComponents([string] $clusterID)
{


    try
    {

        
        $body ="<nwFabricFeatureConfig>
                <resourceConfig>
                <resourceId>$clusterID</resourceId>
                </resourceConfig>
                </nwFabricFeatureConfig>"

        $HostPreparationURI = "/api/2.0/nwfabric/configure"
        $test = http-rest-xml "POST" $HostPreparationURI $body

        write-host "Response for Host preparation is $test"
        
        <#--write-Host "Host Preparation URI is $HostPreparationURI"
        write-Host "XML request for Host Preparation is "$body
        $response = Invoke-WebRequest -Uri $HostPreparationuri -Headers $headers -Method $method -Body $body -ContentType "application/xml"
        $status = [int]$response.StatusCode
        Write-Host "Response status code returned by InstallNVComponents is $Status"
        Write-Host "Response returned by InstallNVComponents is "$response.Content | ConvertTo-XML

        if ($status -ne '200'){
                Write-Error "Error in installing NSX vibs"
                return $false
       }
       return $true--#>
       return $true
    }
    catch 
    {
        write-warning "Exception in installing NSX vibs"
        throw $_
        return $false 
    } 

}




<#-----STEPS FOR HOST PREPARATION-----#>


try
{
    $clusterobj = Get-Cluster -Name $cluster
    #$clusterId = $clusterobj.Id.TrimStart("ClusterComputeResource-")
    $clusterId = $clusterobj.ExtensionData.MoRef.Value
    write-Host "Cluster name is "$clusterobj.Name
    write-Host "Cluster Id is "$clusterId
    
    $return = InstallNVComponents $clusterId
    if( $return -eq $false)
    {
        Write-Error " Unable to install NSX vibs in Cluster $cluster"
        return $false
    }
}
catch
{
    Write-Error "Exception in installing NSX vibs in cluster $cluster"
    return $false
}
    
Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false
