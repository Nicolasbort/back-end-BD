var cpf = document.querySelector("input[name='cpf']");
var rg = document.querySelector("input[name='rg']");

cpf.addEventListener("blur", function(){
   if(cpf.value) cpf.value = cpf.value.match(/.{1,3}/g).join(".").replace(/\.(?=[^.]*$)/,"-");
});


rg.addEventListener("blur", function(){
   if(rg.value) rg.value = rg.value.replace(/\D/g,"").replace(/(\d{2})(\d{3})(\d{3})(\d{1})$/,"$1.$2.$3-$4");
});