var client = mqtt.connect("ws://0.0.0.0:9001");

const MAIN_CHANEL = "farm/farm1";
const INSTANT_CHANEL = "/instants";
const POSITION_CHANEL = "/position";
const PING_CHANEL = "/ping";
const EMERGENCY_CHANEL = "/emergency";

client.subscribe(MAIN_CHANEL);
client.subscribe(MAIN_CHANEL + POSITION_CHANEL);
client.subscribe(MAIN_CHANEL + PING_CHANEL);
client.subscribe(MAIN_CHANEL + EMERGENCY_CHANEL);

let emergency_btn = $("#emergency_btn");
let unlock_btn = $("#unlock_btn");

client.on("message", function (topic, payload) {
    switch (topic) {
        case MAIN_CHANEL + POSITION_CHANEL:
            update_position(JSON.parse(payload));
            break;
        case MAIN_CHANEL + EMERGENCY_CHANEL:
            update_EStatus(parseInt(payload));
        case MAIN_CHANEL:
            break;
        default:
            console.log([topic, payload].join(": "));
    }
});

function update_position(val) {
    $("#position_show").text("x: " + val["X"] + " y: " + val["Y"] + " z: " + val["Z"]);
}

function update_EStatus(val) {
    switch (val) {

        case 0:
            emergency_btn.show();
            unlock_btn.hide();
            break;
        case 1:
            emergency_btn.hide();
            unlock_btn.show();
            break;

    }
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

emergency_btn.click(function() {
    client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["emergency"]]));
});
unlock_btn.click(function() {
    client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["reset_emergency"]]));
});

function distChange(sender) {
    let val = "";
    if (typeof sender.target != "undefined") val = $(sender.target).val();
    else val = sender;

    $(".distcontroller").val(val);
}

$(document).ready(function () {
    distChange(10);
    update_EStatus(0);
});