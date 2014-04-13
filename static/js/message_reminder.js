$(document).ready(function (){
    message_status();
})


function message_status()
{
    $.getJSON("/message/get_status/", function(data)
	{
	    //var response = JSON.parse(data);
		if (data.status == "new_message")
		{
		    $("#message_icon").removeAttr("style");
		    $("#message_badge").removeAttr("style");
		}
	});
}