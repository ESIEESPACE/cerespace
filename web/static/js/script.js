var client = mqtt.connect("ws://0.0.0.0:9001");

const MAIN_CHANEL = "farm/farm1";
const INSTANT_CHANEL = "/instants";
const POSITION_CHANEL = "/position";
const PING_CHANEL = "/ping";
const EMERGENCY_CHANEL = "/emergency";
const PARAMS_CHANEL = "/params";

var coord = [0, 0, 0];

client.subscribe(MAIN_CHANEL);
client.subscribe(MAIN_CHANEL + POSITION_CHANEL);
client.subscribe(MAIN_CHANEL + PING_CHANEL);
client.subscribe(MAIN_CHANEL + EMERGENCY_CHANEL);
client.subscribe(MAIN_CHANEL + PARAMS_CHANEL);

let emergency_btn = $("#emergency_btn");
let unlock_btn = $("#unlock_btn");

let go_coord_btn = $("#go_coord");

let homing_btn = [$("#home_x_btn"), $("#home_y_btn"), $("#home_z_btn")];

let xcoord = $("#xcoord");
let ycoord = $("#ycoord");
let zcoord = $("#zcoord");
let xval = $("#xval");
let yval = $("#yval");
let zval = $("#zval");

client.on("message", function (topic, payload) {
    switch (topic) {
        case MAIN_CHANEL + POSITION_CHANEL:
            update_position(JSON.parse(payload));
            break;
        case MAIN_CHANEL + EMERGENCY_CHANEL:
            update_EStatus(parseInt(payload));
            break;
        case MAIN_CHANEL + PARAMS_CHANEL:
            let data = JSON.parse(payload);
            update_params(data["P"], data["V"]);
            break;
        case MAIN_CHANEL:
            break;
        default:
            console.log([topic, payload].join(": "));
    }
});

function update_position(val) {
    coord = [val["X"], val["Y"], val["Z"]];

    xcoord.text(val["X"]);
    ycoord.text(val["Y"]);
    zcoord.text(val["Z"]);
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
            send_relative_go([distance_value, 0, 0], INSTANT_CHANEL);
            break;
        case "backward":
            send_relative_go([-distance_value, 0, 0], INSTANT_CHANEL);
            break;
        case "right":
            send_relative_go([0, distance_value, 0], INSTANT_CHANEL);
            break;
        case "left":
            send_relative_go([0, -distance_value, 0], INSTANT_CHANEL);
            break;
        case "up":
            send_relative_go([0, 0, distance_value], INSTANT_CHANEL);
            break;
        case "down":
            send_relative_go([0, 0, -distance_value], INSTANT_CHANEL);
            break;
        case "take_photo":
            client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["take_photo"]]));
            break;
    }
});

function send_relative_go(rel_coord, chanel) {
    let temp_coord = [0, 0, 0];
    for (let i = 0; i < 3; i++) {
        temp_coord[i] = coord[i] + rel_coord[i];
    }
    client.publish(MAIN_CHANEL + chanel, JSON.stringify([["go", temp_coord]]));
}

$(".distcontroller").change(distChange);
$("#distselect").on('input', distChange);

emergency_btn.click(function () {
    client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["emergency"]]));
});
unlock_btn.click(function () {
    client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["reset_emergency"]]));
});

go_coord_btn.click(function () {
    let temp_coord = [xval.val(), yval.val(), zval.val()];
    client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["go", temp_coord]]))
});

homing_btn[0].click(function () {
    client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["home", "X"]]))
});

homing_btn[1].click(function () {
    client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["home", "Y"]]))
});

homing_btn[2].click(function () {
    client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["home", "Z"]]))
});

function distChange(sender) {
    let val = "";
    if (typeof sender.target != "undefined") val = $(sender.target).val();
    else val = sender;

    $(".distcontroller").val(val);
}

$(document).ready(function () {
    update_EStatus(0);
    if (document.documentURI.includes("controller")) {
        distChange(10);

    }
    else if (document.documentURI.includes("settings")) {
        client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify([["report_params"]]))
        init_settings();
    }
});