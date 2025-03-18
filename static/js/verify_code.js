$(function() {
    // 定义绑定验证按钮点击事件的函数
    function bindVerifyCaptchaBtnClick() {
        $("#compare-btn").click(function (event) {
            let $this = $(this);
            let email = $("input[name='email']").val();
            let captcha = $("#captcha").val();


            // 发送验证请求
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
                    alert("验证请求失败，请重试！");
                }
            });
        });
    }


    bindVerifyCaptchaBtnClick();
});