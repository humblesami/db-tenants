$(function(){
    if(!document.querySelector('#subscription_form select[name="package"]'))
    {
        return;
    }
    document.querySelector('#subscription_form select[name="package"]').onchange=function() {
        let package_id = this.value;
        let el_due_amount = $('#subscription_form input[name="price"]');
        if(!package_id){
            el_due_amount.val(0);
            return;
        }
        let options = {
            beforeSend: function(a, b){
                //console.log(b.url);
            },
            url: '/package/charges',
            data : {package_id: package_id},
            success:function(data){
                el_due_amount.val(data);
            },
            error:function(er){
                console.log(er);
            }
        };
        $.ajax(options);
    }
});
name="package"