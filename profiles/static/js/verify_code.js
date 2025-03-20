$(function() {
    // Define function to bind verification button click event
    function bindVerifyCaptchaBtnClick() {
        $("#compare-btn").click(function (event) {
            let $this = $(this);
            let email = $("input[name='email']").val();
            let captcha = $("#captcha").val();


            // Send verification request
            $.ajax({
                url: "{% url 'verify' %}",
                method: 'GET',
                data: {
                    email: email,
                    captcha: captcha
                },
                success: function(result) {

                    alert(result.message);
                    if (result.code === 200) {

                        console.log("verification code is right！");
                        $("#new-email-container").show();
                    } else {

                        console.log("verification code is wrong！");
                    }
                },
                error: function(error) {

                    console.log(error);
                    alert("Verification request failed, please try again!");
                }
            });
        });
    }


    bindVerifyCaptchaBtnClick();
});
