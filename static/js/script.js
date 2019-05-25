var client = mqtt.connect("ws://0.0.0.0:9001");

client.subscribe("farm/farm1");

client.on("message", function (topic, payload) {
    console.log([topic, payload].join(": "));
});

$(".btn-control").click(function (event) {
    let btn = $(event.target);
    let cmd = ["go"];
    let value = $("#distselect").val();
    switch (btn.attr("id")) {
        case "fw":
            cmd.push([value, 0, 0]);
            break;
        default:
            break;
    }
});

$(".distcontroller").change(distChange);
$("#distselect").on('input', distChange);

function distChange(sender) {
    let val = "";
    if (typeof sender.target != "undefined") val = $(sender.target).val();
    else val = sender;

    console.log(val);
    $(".distcontroller").val(val);

}

$(document).ready(distChange(10));