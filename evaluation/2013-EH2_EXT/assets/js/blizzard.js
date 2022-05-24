$(document).ready(function() {

    $("#native_language").removeAttr('required');
    $("#native_language_div").hide();

    $("#english_dialect").removeAttr('required');
    $("#english_dialect_div").hide();

    $("#english_level").removeAttr('required');
    $("#english_level_div").hide();


    $("#previous_challenges").removeAttr('required');
    $("#previous_challenges_div").hide();


    $('select[name=english_native]').change(function() {
        if($(this).val() == "Y") {
            $("#english_dialect_div").show();
            $("#english_dialect").attr('required', '');


            $("#native_language").removeAttr('required');
            $("#native_language_div").hide();

            $("#english_level").removeAttr('required');
            $("#english_level_div").hide();
        } else {
            $("#native_language_div").show();
            $("#native_language").attr('required', '');
            $("#english_level_div").show();
            $("#english_level").attr('required', '');


            $("#english_dialect").removeAttr('required');
            $("#english_dialect_div").hide();
        }
    });



    $('select[name=participated_blizzard]').change(function() {
        if($(this).val() == "Y") {
            $("#previous_challenges_div").show();
            $("#previous_challenges").attr('required', '');
        } else {
            $("#previous_challenges").removeAttr('required');
            $("#previous_challenges_div").hide();
        }
    });
});
