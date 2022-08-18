require([
    'jquery',
    'splunkjs/mvc/simplexml/ready!'
], function($, mvc, splunk_js_sdk) {

    var ck_div = $(".ck_div_input_fields");

    var add_credential_keys = $(".add_credential_keys");

    $(add_credential_keys).click(function(e) {
        e.preventDefault();

        var nothing = ""
        var name = ""
        var s3_endpoint = ""
        var s3_access_key = ""
        var s3_secret_key = ""
        var s3_region = ""
        var s3_bucket = ""

        var htmlout = '<div name="ck_input"><p class="helpText"><br>name<br><input type="text" size="20" name="vals[]" value="' + name + '"/><a href="#" class="remove_field"> Remove</a>'
        htmlout = htmlout + '<br>s3 endpoint (https://s3.amazonaws.com for S3)<br><input type="text" size="20" name="vals[]" value="' + s3_endpoint + '"/>'
        htmlout = htmlout + '<br>s3 bucket name<br><input type="text" size="20" name="vals[]" value="' + s3_bucket + '"/>'
        htmlout = htmlout + '<br>s3 region<br><input type="text" size="20" name="vals[]" value="' + s3_region + '"/>'
        htmlout = htmlout + '<br>s3 access key<br><input type="text" size="20" name="vals[]" value="' + s3_access_key + '"/>'
        htmlout = htmlout + '<br>s3 secret key<br><input type="password" size="20" name="vals[]" value="' + s3_secret_key + '"/></div>'
        
        $(ck_div).append(htmlout);
    });



    $(ck_div).on("click", ".remove_field", function(e) {
        e.preventDefault();
        $(this).parent('p').parent('div').remove();
    });

    $.ajax({
        type: "GET",
        url: "../../../../en-US/splunkd/__raw/services/cloudbackup/cloudbackupsetup/cloudbackup?output_mode=json",
        success: function(text) {

            var credentials_json = text;


            configs = credentials_json['entry'][0]['content']['configs'];
            configs = JSON.parse(configs);

            var ck_div = $(".ck_div_input_fields");

            for (var i = 0; i < configs.length; i++) {
                console.log("listing loop");
                var nothing = "";
                console.log(configs[i]);
                var htmlout = '<div name="ck_input"><p class="helpText"><br>name:<br><input autocomplete="off"  type="text" size="20" name="vals[]" value="' + configs[i]['name'] + '"/><a href="#" class="remove_field"> Remove</a>'
                htmlout  = htmlout + '<br>s3 endpoint (https://s3.amazonaws.com for S3)<br><input autocomplete="off"  type="text" size="20" name="vals[]" value="' + configs[i]['s3_endpoint'] + '"/>'
                htmlout  = htmlout + '<br>s3 bucketname<br><input autocomplete="off"  type="text" size="20" name="vals[]" value="' + configs[i]['s3_bucket'] + '"/>'
                htmlout  = htmlout + '<br>s3 region<br><input autocomplete="off"  type="text" size="20" name="vals[]" value="' + configs[i]['s3_region'] + '"/>'
                htmlout  = htmlout + '<br>s3 key<br><input autocomplete="off"  type="text" size="20" name="vals[]" value="'+ configs[i]['s3_access_key'] + '"/>'
                htmlout  = htmlout + '<br>s3 secret<br><input autocomplete="off"  type="password" size="20" name="vals[]" value="'+ configs[i]['s3_secret_key'] +'"/></p></div>'
                $(ck_div).append(htmlout);
            }
        },
        error: function() {
        }
    });

    var submit_button = $("#ck_submit_button");
    var cancel_button = $("#ck_cancel_button");

    $(submit_button).click(function(e) {
        e.preventDefault();

        console.log("my fields..");
        var credential_key_string = "";
        var credential_string = "";

        var s3config = new Object();

        var n = 0;

        out = [];
        i = 0; // index for objects
        $('input[name^="vals"]').each(function() {
            
            if (n % 6 == 0) {
                s3config['name'] = $(this).val();
                console.log("name: " + s3config['name'] + " found");
            } else if (n % 6 == 1 ) {
                if ($(this).val().length == 0) {
                    config.log("setting as aws default");
                    s3config['s3_endpoint'] = "https://s3.amazonaws.com";
                } else {
                    s3config['s3_endpoint'] = $(this).val();
                }
            } else if (n % 6 == 2 ) {
                s3config['s3_bucket'] = $(this).val();
            } else if (n % 6 == 3 ) {
                s3config['s3_region'] = $(this).val();
            } else if (n % 6 == 4 ) {
                s3config['s3_access_key'] = $(this).val();
            } else if (n % 6 == 5 ) {
                s3config['s3_secret_key'] = $(this).val();
                s3config['type'] = "s3"
                out.push(JSON.stringify(s3config));
                //out.push(s3config);
                console.log("adding to out");
            }
            n++;
        });


        strtmp = "[" + out.toString() + "]";
        mydata = "configs=" + btoa(strtmp);
        // // could be used to directly send it to endpoint.
        // console.log("sending data.. ");
        // console.log(mydata);

        console.log(e)
        $.ajax({
            type: "POST",
            url: "../../../../en-US/splunkd/__raw/services/cloudbackup/cloudbackupsetup/cloudbackup",
            data: mydata,
            success: function(text) {
                console.log("successful ");
                //window.location.href = '../cloud_backup/overview';
            },

            // error: function() {

            // }
        });


        //$('div[name^="ck_input"]').remove();
        $(".ck_div_input_fields").append('<div name="saving_creds_msg" style="text-align: center;"><p class="helpText"><h3>saved...</h3></p></div>');




    });

    $(cancel_button).click(function(e) {
        e.preventDefault();
        $('div[name^="ck_input"]').remove();
        //window.location.href = '../cloud_backup/overview';

    });




});