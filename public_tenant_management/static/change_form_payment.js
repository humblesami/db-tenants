$(function(){
    if(!document.querySelector('#payment_form select[name="subscription"]'))
    {
        return;
    }
    let el_due_amount = $('#payment_form input[name="due_amount"]').attr('readonly', 'readonly');
    document.querySelector('#payment_form select[name="subscription"]').onchange=function() {
        let subscription_id = this.value;
        if(!subscription_id){
            el_due_amount.val(0);
            return;
        }
        let module_url = '/subscription'
        let host_url = window.location.protocol + '//' + window.location.host;
        let api_url = '/subscription/charges';
        let req_url = host_url + module_url + api_url;
        let options = {
            beforeSend: function(a, b){
                console.log(b.url);
            },
            url: req_url,
            data : {subscription_id: subscription_id},
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