$(document).ready(function (){
    reply();
})



function reply(){
    $("#reply_submit").click(function (){
        form = $("form#reply_form");
        messenger = Messenger();

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function (data){
                var response = JSON.parse(data);
                if(response.status == "success"){
                    messenger.post({
                        message: "发表成功",
                        type: "success"
                    })

                    //清空这个编辑器的textarea 蛋疼。。
                    editor.setValue("", false);

                    //构造ajax插入的html
                    var html = '<div class="panel panel-info"><div class="panel-heading">'
                    html += (response.username + '&nbsp;&nbsp;|&nbsp;&nbsp;' + response.time)
                    html += ('<a href="javascript:void(0)" class="reply" onclick="reply_comment(' + "'" + response.username + "'" + ')">回复</a>')
                    html += '</div><div class="panel-body">'
                    html += (response.content + '</div></div>')

                    $("div.replies").append(html)
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


