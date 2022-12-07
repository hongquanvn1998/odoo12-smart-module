$(function(){  

    const POD_MIN_HEIGHT = 20*$("#page-left").height()/100  
 
    // $("#order-items").resizable({
    //     handles:'n,s'
    // });
    // $('#order-items').resize(function(){
    //     if ($('#product-items').height()<POD_MIN_HEIGHT){
    //         $('#product-items').height(POD_MIN_HEIGHT) 
    //     }
    //     if ($('#order-items').height()<$("#order-cart-list").height()+65){
    //         $('#order-items').height($("#order-cart-list").height()+65) 
    //     }

    //         $('#product-items').height($("#page-left").height()-$("#order-items").height()); 
   
    // });
    // $(window).resize(function(){
    //     if ($('#product-items').height()<POD_MIN_HEIGHT){
    //         $('#product-items').height(POD_MIN_HEIGHT) 
    //     }
    //     if ($('#order-items').height()<$("#order-cart-list").height()+65){
    //         $('#order-items').height($("#order-cart-list").height()+65) 
    //     }

    // $('#product-items').height($("#page-left").height()-$("#order-items").height()); 
    // //  $('#div1').height($("#parent").height()); 
    // });
    var minHeight = 10;
    var top1H, bottom1H;
    var right1W, left1W;
    const order_items_height = $("#order-items").height()

    $( ".resize-btn" ).draggable({
        axis: "y",
        // containment: 'parent',
        start: function(event, ui) {
        shiftInitial = ui.position.top;
        top1H = $("#order-items").height();
        bottom1H = $("#product-items").height();
        },
        drag: function(event,ui) {
            var shift = ui.position.top;
            let hihi = $('#product-items').height() 
            if ($('#product-items').height()<41){
                $('#product-items').height(41)
                // $('.resize-this').height(41)
            }else if($('#product-items').height() >= 442){
                $("#product-items").height(442);
                $("#order-items").height(order_items_height)
            } else{
                $("#product-items").height(bottom1H - shift + shiftInitial);
            }
            // if ($('#order-items').height()<$("#order-cart-list").height()+65){
            //     $('#order-items').height($("#order-cart-list").height()-65) 
            // }else{
                $("#order-items").height(top1H + shift - shiftInitial);
            // }
            // $('.page-right').height(Math.max(
            //     minHeight,
            //     Math.max(
            //     $('#order-items').height()+$('.resize-btn').height(),
            //     $('#order-items').height()+$('#product-items').height()
            //     )));
        }
    });

    // $('[data-toggle="popover"]').popover({
    //     html : true,
    //     tempalte: '<div class="popover" role="tooltip"><div class="arrow"></div><div class="popover-body"></div></div>',
    //     content: function() {
    //       var content = $(this).attr("data-popover-content");
    //       return $(content).children(".discount-form").html();
    //     }
    //     // title: function() {
    //     //   var title = $(this).attr("data-popover-content");
    //     //   return $(title).children(".popover-heading").html();
    //     // }
    // }); 


    $('[data-toggle="popover"]').on('show.bs.popover',function () {
        $('[data-toggle="popover"]').popover('hide');
    });    

    // $("html").on("mouseup", function (e) {
    //     var l = $(e.target);
    //     if (l[0].className.indexOf("popover") == -1) {
    //         $(".popover").each(function () {
    //             $(this).popover("hide");
    //         });
    //     }
    // });

})
$('body').on('click', function (e) {
    $('[data-toggle=popover]').each(function () {
        // hide any open popovers when the anywhere else in the body is clicked
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
});
// $(document).mouseup(function(e) 
// {
//     var container = $(".autocomplete-prod");

//     // if the target of the click isn't the container nor a descendant of the container
//     if (!container.is(e.target) && container.has(e.target).length === 0){
//         $(".output-complete-prod").hide();
//     }else{
//         $(".output-complete-prod").show();
//     }
// });
// $(document).mouseup(function(e) 
// {
//     var container = $(".autocomplete-customer");

//     // if the target of the click isn't the container nor a descendant of the container
//     if (!container.is(e.target) && container.has(e.target).length === 0){
//         $(".output-complete-customer").hide();
//     }else{
//         $(".output-complete-customer").show();
//     }
// });

