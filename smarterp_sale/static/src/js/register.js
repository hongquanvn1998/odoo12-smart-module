odoo.define('smarterp_sale.register', function (require) {
  "use strict";
  // var form_widget = require('web.form_widgets');
  var core = require('web.core');

  var rpc = require('web.rpc');

  var formatter = new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  });
 
  var user;
  var modules;
  var installApp =[]
  

  var orderItems =[]

  var dependentSelect =   (id) =>{ 
    let dependent; 
    for (let i =0; i< modules.length; i++) {
        if (modules[i].code == id ) { 
            let _depend = modules[i].barcode.split(',') 
        
            dependent = _depend
        }
      }  
      dependent.splice(0,1)  
    return dependent;
  }

  var setOrderItem = (type, id, price=null, quantity=null)=>{
      if(type) { 
        // Add to items
      return  orderItems.push({
          moduleId: id,
          orderPrice: price,
          orderQuantity: quantity
        })  
      } 
      // Remove item
      return orderItems.forEach((item,index)=>{
        if (item.moduleId == id)  {
          orderItems.splice(index,1)
        }
      })



  }

  var setUrlParameter =(type,par)=> {
   
    var url = document.location.href.split('#');
    var params = url[1]?url[1].split('&'):[]

    if (!type) {
      params.forEach((item,i)=>{
        if (item.split('=')[0]=== par) {
          params.splice(i,1)
        }
      })
    } else {
      if (params.length>0){
        let _found = false;
        params.forEach((item,i)=>{
          if (item.split('=')[0]=== par) {
            _found= true;
          }
        })

        if (!_found) {
          params.push(`${par}=on`)
        }

      } else {
        params.push(`${par}=on`)
      }

    }
    
    let app_count =0; 
    let appTotal = 0;

    // var uri = new URL(window.location.search);
    let para = new URLSearchParams(url[1])
    var price_type = para.get('price_by');
    para.set('price_by','updated')

    console.log('Kieu tinh tien: ',price_type)
    params.forEach((item)=>{ 
      if (item.split('=')[0].startsWith('app_')) {
        appTotal += $(`.${price_type}-price-${item.split('=')[0].split('_')[1]}`).html()
         app_count++
      }
    })

    $('#selected_module_total').html(appTotal)


    $('#selected_module_count').html(app_count)
    
    document.location = `${url[0]}#${params.join('&')}`; 
  }

  var setUrlParameterValue = (name, value)=>{
    var url = document.location.href.split('#');
    let params = url[1]?url[1].split('&'):[]
    params.forEach((item,i)=>{
      if (item.split('=')[0]===name) {
        params[i] = `${name}=${value}`
      }
    }) 
    document.location = `${url[0]}#${params.join('&')}`; 
  }

  var setLoadUrlParameter = ()=>{
    var url = document.location.href.split('#');
    var params = [
      'num_user=1',
      'price_by=yearly'
    ]  
    document.location = `${url[0]}#${params.join('&')}`; 
  }



  $(function () {
    setLoadUrlParameter()

    $('#annually-title').click(()=>{
        $('.monthly-price').removeClass('d-block').addClass('d-none')
        $('.annually-price').removeClass('d-none').addClass('d-block')
        setUrlParameterValue('price_by','yearly')
    });

    $('#monthly-title').click(()=>{
      $('.annually-price').removeClass('d-block').addClass('d-none')
      $('.monthly-price').removeClass('d-none').addClass('d-block')
      setUrlParameterValue('price_by','monthly')
  });

    $("#user-count").on('change',(event)=>{
        $('#selected_user_count').html(event.target.value) 
        $('#selected_user_total').html(formatter.format(event.target.value*user.list_price))
        setUrlParameterValue('num_user',event.target.value)
    })


    $(".module-checkbox").on('change',(event)=>{

      if ($(`#${event.target.id}`).prop('checked')== true) {
        setUrlParameter(1,`app_${event.target.id}`)
        let depend = dependentSelect(event.target.id) 
        if (depend) {
          depend.forEach(item=>{
            $(`#${item}`).prop('checked', true);
            setUrlParameter(1,`app_${item}`) 
          })
        } 

      } else {
        setUrlParameter(0,`app_${event.target.id}`)

      }
     
    })




    $("#state").change((event)=>{
      LoadDistricts()
    })

    UserService();
    ProductList();
    var stepper = new Stepper($('.bs-stepper')[0])

    $("#register").click((event) => {

      var form = $("#register_customer_info");
      if (form[0].checkValidity() === false) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.addClass('was-validated');

      if (form[0].checkValidity() === true) {
        EmailValidate().then(res => {
          if (res) {
            stepper.next()
            $('#username').val($('#email').val());
           
          }

        }).catch(err => {

        })
      }

      // Perform ajax submit here... 
    });

    $('#signup-submit').click((event) => {
      var form = $("#register_application");
      if (form[0].checkValidity() === false) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.addClass('was-validated');
      if (form[0].checkValidity() === true) {
        alert("Da ok het roi")
      }

    })
 


  })

  var RegisterCustomer = () => {
    let fullname = $("#fullname").val();
    let state = $("#state").val();
    let district = $("#district").val();
    let address = $("#address").val();
    let phone = $("#phone").val();
    let mobile = $("#mobile").val();
    let email = $("#email").val();
    let taxCode = $("#taxcode").val();
    let isCompany = $("#mode").is(":checked") ? 1 : 0;
    console.log(fullname, state, district, address, phone, mobile, email, taxCode, isCompany)
    $.ajax({
        method: "POST",
        url: "new-customer",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
          jsonrpc: "2.0",
          id: 186000,
          params: {
            fullname: fullname,
            state: state,
            district: district,
            address: address,
            phone: phone,
            mobile: mobile,
            email: email,
            taxcode: taxCode,
            iscompany: isCompany
          }
        })
      })
      .done(function (msg) {
        console.log("Data Saved: ", msg);
      });

  }

  var LoadDistricts = () =>{
    $.ajax({
      method: "POST",
      url: "districts",
      dataType: "json",
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify({
        jsonrpc: "2.0",
        id: 15525500,
        params: {
          state_id: parseInt($('#state').val() )
        }
      })
    })
    .done(function (msg) {
      let selectHtml ='<option> --Quận/huyện-- </option>';
      let _districts = msg['result']
      _districts.forEach(item=>{
          selectHtml+=`<option value="${item.id}"> ${item.name} </option>`
      }) 
      $('#district').html(selectHtml)
    });
  }

  
  var UserService = () => {
    $.ajax({
        method: "POST",
        url: "user-service",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
          jsonrpc: "2.0",
          id: 15525500,
          params: {
            default_code: "user_count" 
          }
        }), 
        success: (msg)=>{ 
          user = msg['result'][0]    
        }
      }) 

  }

  var ProductList = () => {
    $.ajax({
        method: "POST",
        url: "products",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
          jsonrpc: "2.0",
          id: 15525500,
          params: { 
          }
        }), 
        success: (msg)=>{ 
         modules = msg['result']
        }
      }) 

  }



  var CreateDatabase = () => {
    $.ajax({
        method: "POST",
        url: "../web/database/register",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
          jsonrpc: "2.0",
          id: 15525500,
          params: {
            master_pwd: "taoday",
            name: $("#domain").val(),
            login: $("#email").val(),
            password: $("#password").val(),
            phone: $("#mobile").val(),
            lang: "vi_VN",
            country_code: "vn",
            demo: 0
          }
        })
      })
      .done(function (msg) {

      });

  }

  var EmailValidate = () => {
    let promise = new Promise((resolve, reject) => {
      $.ajax({
          method: "POST",
          url: "validate",
          dataType: "json",
          contentType: "application/json; charset=utf-8",
          data: JSON.stringify({
            jsonrpc: "2.0",
            id: 15525500,
            params: {
              email: $("#email").val()
            }
          }),
          error: (xhr, ajaxOptions, thrownError) => {
            reject(thrownError)
          }
        })
        .done(function (msg) {
          resolve(msg)
        });
    })
    return promise;
  }


  var createStepper = () => {

    var form = $("#example-advanced-form").show();

    form.steps({
      headerTag: "h3",
      bodyTag: "fieldset",
      transitionEffect: "slideLeft",
      onStepChanging: function (event, currentIndex, newIndex) {
        // Allways allow previous action even if the current form is not valid!
        if (currentIndex > newIndex) {
          return true;
        }
        // Forbid next action on "Warning" step if the user is to young
        if (newIndex === 3 && Number($("#age-2").val()) < 18) {
          return false;
        }
        // Needed in some cases if the user went back (clean up)
        if (currentIndex < newIndex) {
          // To remove error styles
          form.find(".body:eq(" + newIndex + ") label.error").remove();
          form.find(".body:eq(" + newIndex + ") .error").removeClass("error");
        }
        form.validate().settings.ignore = ":disabled,:hidden";
        return form.valid();
      },
      onStepChanged: function (event, currentIndex, priorIndex) {
        // Used to skip the "Warning" step if the user is old enough.
        if (currentIndex === 2 && Number($("#age-2").val()) >= 18) {
          form.steps("next");
        }
        // Used to skip the "Warning" step if the user is old enough and wants to the previous step.
        if (currentIndex === 2 && priorIndex === 3) {
          form.steps("previous");
        }
      },
      onFinishing: function (event, currentIndex) {
        form.validate().settings.ignore = ":disabled";
        return form.valid();
      },
      onFinished: function (event, currentIndex) {
        alert("Submitted!");
      }
    }).validate({
      errorPlacement: function errorPlacement(error, element) {
        element.before(error);
      },
      rules: {
        confirm: {
          equalTo: "#password-2"
        }
      }
    });

    //  function InstallApp() {
    //     $.ajax({
    //         method: "POST",
    //         url: "",
    //         data: { name: "John", location: "Boston" }
    //       })
    //         .done(function( msg ) {
    //           alert( "Data Saved: " + msg );
    //         });
    //  }

    //    events: {
    //     "click .your_class": "your_function",
    // }


  }




})