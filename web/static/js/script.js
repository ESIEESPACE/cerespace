var client = mqtt.connect("ws://0.0.0.0:9001");

const MAIN_CHANEL = "farm/farm1";
const INSTANT_CHANEL = "/instants";
const POSITION_CHANEL = "/position";
const PING_CHANEL = "/ping";

client.subscribe(MAIN_CHANEL);
client.subscribe(MAIN_CHANEL + POSITION_CHANEL);
client.subscribe(MAIN_CHANEL + PING_CHANEL);

client.on("message", function (topic, payload) {
    switch (topic) {
        case MAIN_CHANEL + POSITION_CHANEL:
            update_position(JSON.parse(payload));
            break;
        case MAIN_CHANEL:
            break;
        default:
            console.log([topic, payload].join(": "));
    }
});

function update_position(val) {
    $("#position_show").text("x: " + val[0] + " y: " + val[1] + " z: " + val[2]);
}

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
            break;
    }
});

function send_go(coord, chanel) {
    client.publish(MAIN_CHANEL + chanel, JSON.stringify([["go", coord]]));
}

$(".distcontroller").change(distChange);
$("#distselect").on('input', distChange);

function distChange(sender) {
    let val = "";
    if (typeof sender.target != "undefined") val = $(sender.target).val();
    else val = sender;

    $(".distcontroller").val(val);
}

$(document).ready(distChange(10));