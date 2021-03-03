(function(){
    let shared_apps = [
        'auth'
    ];
    let public_apps = [
        'public_tenants',
        'public_customers',
        'public_tenant_management',
        'public_tenants',
    ];
    function show_apps(arr){
        for(let app_name of arr)
        {
            let selector = '.app-'+app_name+'.module';
            $(selector).show();
        }
    }
    $(function(){
        let modules_to_show = shared_apps;
        show_apps(modules_to_show);
        let host_name = window.location.host + '';
        let host_url = window.location.protocol +'//' + host_name;
        let arr = host_name.split('.');
        let installed_apps = [];
        if(arr && arr.length){
            console.log(arr[0]);
            if(!arr[0].startsWith('localhost:') && arr[0] != '127')
            {
                let api_url = '/tenant/get-apps';
                let req_url = host_url + api_url;
                let ajax_options = {
                    url: req_url,
                    beforeSend: function(a, b){
                        console.log(b.url);
                    },
                    success: function(res)
                    {
                        if(res.status == 'success')
                        {
                            let tenant_apps = res.data;
                            console.log(tenant_apps);
                            modules_to_show = tenant_apps;
                            show_apps(modules_to_show);
                        }
                    },
                    error: function(er){
                        console.log('error in request ', er)
                    }
                }
                $.ajax(ajax_options);
            }
            else{
                modules_to_show = public_apps;
                show_apps(modules_to_show);
            }
        }
    })
})()
