$(".btn-control").click(function (event) {
    console.log(sender)
    let btn = $(event.target)
    if(btn.text() == "Forawd");
});

$(".distcontroller").change(distChange);
$("#distselect").on('input', distChange);

function distChange(sender) {
    let val = "";
    if(typeof sender.target != "undefined") val = $(sender.target).val();
    else val = sender;

    console.log(val);
    $(".distcontroller").val(val);

}

$(document).ready(distChange(10));