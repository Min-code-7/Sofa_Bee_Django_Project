$(function() {
    function bindCaptchaBtnClick() {
        $("#captcha-btn").click(function (event) {
            let $this = $(this);
            let email = $("input[name='email']").val();
            if (!email) {
                alert("Please enter valid email");
                return;
            }
            $this.off('click');
            $.ajax('captcha?email='+email,{
                method: 'GET',
                success: function(result) {
                    console.log(result);
                },
                fail:function (error){
                    console.log(error);
                }
            })
            let countdown = 60;
            let timer = setInterval(function () {
                if (countdown <= 0) {
                    $this.text('get verification code');
                    //$this.on('click');
                    clearInterval(timer);
                    bindCaptchaBtnClick();

                } else {
                    $this.text(countdown + 's');
                    countdown--;
                }
            }, 1000)
        });
    }
    bindCaptchaBtnClick();
});