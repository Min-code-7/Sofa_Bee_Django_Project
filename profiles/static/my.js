function f1(){
    const name = 111;
    var num=name.length;
    alert(num);
}
function show()
  {
    const tag = document.getElementById("content");
    const str = tag.innerText;
    for(var i=0;i<str.length;i++){
        const firstChar = str[0];
        const other = str.substring(1, str.length);
        const newstr = other + firstChar;
        tag.innerText=newstr;
    }
    //console.log(newstr);
  }



