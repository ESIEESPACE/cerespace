var client = mqtt.connect("ws://0.0.0.0:9001");

client.subscribe("farm/farm1");

client.on("message", function (topic, payload) {
    console.log([topic, payload].join(": "));
});

$(".btn-control").click(function (event) {
    let btn = $(event.target);
    let cmd = ["go"];
    let value = parseInt($("#distselect").val());
    switch (btn.attr("id")) {
        case "fw":
            cmd.push([value, 0, 0]);
            break;
        case "bw":
            cmd.push([-value, 0, 0]);
            break;
        case "rg":
            cmd.push([0, value, 0]);
            break;
        case "lf":
            cmd.push([0, -value, 0]);
            break;
        case "up":
            cmd.push([0, 0, value]);
            break;
        case "down":
            cmd.push([0, 0, -value]);
            break;
        default:
            break;
    }

    client.publish("farm/farm1/instants", JSON.stringify([cmd]))
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