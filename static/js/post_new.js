$(document).ready(function (){
    post_new();
})

function post_new(){
    $("#post_new_submit").click(function (){
        form = $("form#post_new_form");
        messenger = Messenger();

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function (data){
                var response = JSON.parse(data);
                if(response.status == "success"){
                    messenger.post({
                        message: "提交成功",
                        type: "success"
                    })
                    window.location.href=response.redirect
                }
                else if(response.status == "error")
                    messenger.post({
                        message: response.content,
                        type: "error"
                    })
            },
        });
        return false;
    })
}


