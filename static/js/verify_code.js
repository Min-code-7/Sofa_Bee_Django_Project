$(function() {
    // 定义绑定验证按钮点击事件的函数
    function bindVerifyCaptchaBtnClick() {
        $("#compare-btn").click(function (event) {
            let $this = $(this);  // 获取当前按钮的 jQuery 对象
            let email = $("input[name='email']").val();  // 获取邮箱
            let captcha = $("#captcha").val();  // 获取用户输入的验证码


            // 发送验证请求
            $.ajax({
                url: '/verify_captcha/',  // 验证验证码的接口
                method: 'GET',
                data: {
                    email: email,
                    captcha: captcha
                },
                success: function(result) {
                    // 验证成功
                    alert(result.message);  // 显示验证结果
                    if (result.code === 200) {
                        // 验证成功后的逻辑
                        console.log("验证码正确！");
                        $("#new-email-container").show();
                    } else {
                        // 验证失败后的逻辑
                        console.log("验证码错误！");
                    }
                },
                error: function(error) {
                    // 请求失败
                    console.log(error);
                    alert("验证请求失败，请重试！");
                }
            });
        });
    }

    // 绑定验证按钮点击事件
    bindVerifyCaptchaBtnClick();
});