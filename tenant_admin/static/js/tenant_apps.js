$('body').append('<div id="app-hider"><style>.module[class^="app-"]{display:none;}</style></div>');

(function(){
    function show_apps(arr){
        for(let app_name of arr)
        {
            let app_name_ar = app_name.split('.');
            let last_part = app_name_ar[app_name_ar.length-1];
            if(last_part != 'authtoken')
            {
                let selector = '.app-'+last_part+'.module';
                $(selector).show();
            }
        }
    }

    $(function(){
        let is_sub_domain = get_is_sub_domain();
        let host_url = window.location.protocol +'//' + window.location.host;
        let installed_apps = [];

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
                    let apps_data = res.data;
                    console.log(apps_data, is_sub_domain);
                    show_apps(apps_data.shared_apps);
                    if(is_sub_domain)
                    {
                        show_apps(apps_data.tenant_apps);
                    }
                    else{
                        show_apps(apps_data.public_apps);
                    }
                }
            },
            error: function(er){
                console.log('error in request ', er);
                $('#app-hider').remove();
            }
        }
        $.ajax(ajax_options);
    })


    function get_domain()
    {
        var firstDot = window.location.hostname.indexOf('.');
        var tld = ".net";
        var isSubdomain = firstDot < window.location.hostname.indexOf(tld);
        var domain;
        if (isSubdomain) {
            domain = window.location.hostname.substring(firstDot == -1 ? 0 : firstDot + 1);
        }
        else {
          domain = window.location.hostname;
        }
        return domain;
    }

    function get_is_sub_domain(){
        let host_name = window.location.host + '';
        let arr = host_name.split('.');
        let is_sub_domain = false;
        let domain = get_domain();
        if(arr && arr.length && arr.length > 1){
            if(arr.length == 2)
            {
                arr[1].startsWith('localhost')
                {
                    is_sub_domain = true;
                }
            }
            else{
                let host_name_after_first_dot = host_name.replace(arr[0]);
                if(host_name_after_first_dot == domain)
                {
                    is_sub_domain = true;
                }
            }
        }
        return is_sub_domain;
    }
})()
