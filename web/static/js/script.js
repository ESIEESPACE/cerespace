var client = mqtt.connect("ws://0.0.0.0:9001");

const MAIN_CHANEL = "farm/farm1";
const INSTANT_CHANEL = "/instants";

client.subscribe(MAIN_CHANEL);

client.on("message", function (topic, payload) {
    console.log([topic, payload].join(": "));
});

$(".btn-control").click(function (event) {
    let btn = $(event.target);
    let distance_value = parseInt($("#distselect").val());

    switch (btn.attr("id")) {
        case "forward":
            send_go([distance_value, 0, 0], INSTANT_CHANEL);
            break;
        case "backward":
            send_go([-distance_value, 0, 0], INSTANT_CHANEL);
            break;
        case "right":
            send_go([0, distance_value, 0], INSTANT_CHANEL);
            break;
        case "left":
            send_go([0, -distance_value, 0], INSTANT_CHANEL);
            break;
        case "up":
            send_go([0, 0, distance_value], INSTANT_CHANEL);
            break;
        case "down":
            send_go([0, 0, -distance_value], INSTANT_CHANEL);
            break;
        case "take_photo":
            client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["take_photo"]]));
        default:
            break;
    }
});

function send_go(coord, chanel) {
    client.publish(MAIN_CHANEL + chanel, JSON.stringify([["go", coord]]))
}

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