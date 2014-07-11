(function($) {
     $(document).ready(function() {
           $('.btn-add_to_cart').on('click', function(){
                product_id = $(this).data('product_id');
                $.ajax({
                  url: portal_url+'/'+'@@add_to_cart?pid='+product_id,
                  success: function(data){
                    $('#cart-frame').html(data);
                  }
                });
           })

          // initializing cart
          $.ajax({
            url: portal_url+'/'+'@@add_to_cart',
            success: function(data){
              $('#cart-frame').html(data);
            }
          });

          // payment
          $('#payment-form').on('submit', function(e){
            // disabling form
            $(e).css('opacity', 0.2);
            $.ajax({
              type: "POST",
              url: portal_url+'/'+'@@checkout-do',
              data: $("#payment-form").serialize(),
              success: function(data, textStatus, jqXHR){
                  $("#payment-form").html(data)
                },
              //dataType: dataType
            });
            e.preventDefault(); //STOP default action
            e.unbind();

          })
     })
})(jQuery);