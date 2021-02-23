$(function(){
    let host = window.location.host+'';
    let arr = host.split('.');
    if(arr && arr.length){
        if(!arr[0].startsWith('localhost:') && arr[0] != '127')
        {
            let tenant_app_dom = document.querySelector('.app-tenants.module');
            if(tenant_app_dom)
            {
                tenant_app_dom.style.display = 'none';
            }
        }
    }
})