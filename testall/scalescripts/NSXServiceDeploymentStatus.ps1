param($index,$servicename)
. ".\HttpRest.ps1"
Add-PSSnapin vmware.vimautomation.core
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!

$cluster = "ScaleCluster"+$index




#$headers = @{Authorization = $basicAuthValue;Accept='application/xml'}


<#-----FUNCTION TO GET DISK RESOURCE FROM FREENAS SERVER-----#>
Function getServiceDeploymentStatus([string] $clusterID, [string] $serviceName)
{
    $progressStatusflag = $false
    
    $getServiceDeploymentStatusURI = "/api/2.0/si/deploy/cluster/"+$clusterId
    Write-host "Service deployment Status URI is $getServiceDeploymentStatusURI"
    $test = http-rest-xml "GET" $getServiceDeploymentStatusURI
    $deployedServices = $test.deployedServices

    $serviceDeployedStatus = $false
    Foreach ($deployedService in $deployedServices.deployedService) 
    {
        $deployedServiceName = $deployedService.serviceName
       
        
        if( $deployedServiceName -eq $serviceName)
        {
            $progressStatus = $deployedService.progressStatus
            $deploymentUnitID = $deployedService.deploymentUnitId
            write-host "Deployment unit ID is "$deployedService.deploymentUnitId
            return $progressStatus,$deploymentUnitID
           
        }
       
    }
    
   
}

<#-----FUNCTION TO GET DISK RESOURCE FROM FREENAS SERVER-----#>
Function fetchAlarm([string] $deploymentUnitID)
{
    $progressStatusflag = $false
    
    $getAlarmsURI = "/api/2.0/services/alarms/"+$deploymentUnitID
    Write-host "Alarms URI is $getAlarmsURI"
    $response = http-rest-xml "GET" $getAlarmsURI
    
    $systemAlarms = $response.systemAlarms
   
    Foreach ($systemAlarm in $systemAlarms.systemAlarm) 
    {
        $target = $systemAlarm.target
        $message = $systemAlarm.message
        $targetName = $target.name
        write-warning "System Alarm message is '$message',target is '$targetName'"
    } 
    return $response
   
}

<#-----FUNCTION TO GET DISK RESOURCE FROM FREENAS SERVER-----#>
Function resolveAlarm([xml] $alarmRequest)
{
 
    $body = $alarmRequest.DocumentElement.OuterXml

    write-debug "Alarm body is $body"
    
    $resolveAlarmURI = "/api/2.0/services/alarms?action=resolve"

    Write-host "Resolve Alarms URI is $resolveAlarmURI"
    $response = http-rest-xml "POST" $resolveAlarmURI $body
    
   
    write-host "Response for Alarm resolution is $response"
   
}


<#-----STEPS FOR CHECKING NSX HOST PREPARATION AND FIREWALL STATUS-----#>


try
{
     "## Fetching NSX Cluster $cluster MoRef ..."
    $cluster_obj = Get-Cluster $cluster
    
    $cluster_moref = $cluster_obj.ExtensionData.MoRef.Value
    "-> cluster ID : $cluster_moref"
    
    do {

        $status = getServiceDeploymentStatus $cluster_moref $servicename
        $progressStatus = $status[0]
        $deploymentUnitID = $status[1]

        write-host "progressStatus returned is $progressStatus"
        if( $progressStatus -eq "SUCCEEDED" )
        {
            Write-host " $servicename deployment status is UP in cluster $cluster" -ForegroundColor Green
            
        }
        elseif( $progressStatus -eq "FAILED" )
        {
            Write-warning " NSX $servicename deployment status is FAILED in cluster $cluster"
            Write-host " NSX $servicename deployment unit ID for cluster $cluster is $deploymentUnitID"
            $response = fetchAlarm $deploymentUnitID
            
            resolveAlarm $response
           
            
        }
        elseif( $progressStatus -eq "IN_PROGRESS" )
        {
            Write-host " $servicename deployment status is 'ENABLING' in cluster $cluster, polling .." -ForegroundColor Yellow
            
        }
        
        sleep 30
    } while ( ($status[0] -eq "IN_PROGRESS") -or ($status[0] -eq "FAILED"))
}
catch
{
    Write-Error "Exception in retrieving $servicename deployment Status in cluster $cluster"
    return $false
}
    
Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false

