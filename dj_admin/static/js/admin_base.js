(function(){
    let modules_to_show = [
        'auth'
    ];

    function show_apps(arr){
        for(let app_name of arr)
        {
            let selector = '.app-'+app_name+'.module';
            $(selector).show();
        }
    }
    $(function(){
        show_apps(modules_to_show);
        let host = window.location.host+'';
        let arr = host.split('.');
        let installed_apps = [];
        if(arr && arr.length){
            if(!arr[0].startsWith('localhost:') && arr[0] != '127')
            {
            }
            else{
                modules_to_show = [
                    'public_tenants',
                    'public_customers',
                    'public_tenant_management',
                    'public_tenants',
                ];
                show_apps(modules_to_show);
            }
        }
    })

})()
