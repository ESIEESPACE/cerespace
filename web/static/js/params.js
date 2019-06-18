let settings = {
    11: $("#timeout_x"),
    12: $("#timeout_y"),
    13: $("#timeout_z"),

    15: $("#kactive_x"),
    16: $("#kactive_y"),
    17: $("#kactive_z"),

    18: $("#homeaboot_x"),
    19: $("#homeaboot_y"),
    20: $("#homeaboot_z"),

    21: $("#invertendp_x"),
    22: $("#invertendp_y"),
    23: $("#invertendp_z"),

    45: $("#stopahome_x"),
    46: $("#stopahome_y"),
    47: $("#stopahome_z"),

    61: $("#minspd_x"),
    62: $("#minspd_y"),
    63: $("#minspd_z"),

    71: $("#maxspd_x"),
    72: $("#maxspd_y"),
    73: $("#maxspd_z"),

    141: $("#nrsteps_x"),
    142: $("#nrsteps_y"),
    143: $("#nrsteps_z"),
};

function init_settings() {
        for (let index in settings) {
        settings[index].change(function () {
            let val;
            if (settings[index].attr("type") === "checkbox") {
                if (settings[index].prop("checked")) val = 1;
                else val = 0;
            } else {
                val = settings[index].val();
            }
            let sende = [["writeparam", index, val]];

            client.publish(MAIN_CHANEL + INSTANT_CHANEL, JSON.stringify(sende));

        });
    }
}



function update_params(param, val) {
    param = parseInt(param);
    val = parseFloat(val);
    let input = settings[param];
    if (input === undefined) return;
    else if (input.attr("type") === "checkbox") {
        input.prop("checked", val);
    } else {
        input.val(val);
    }
}