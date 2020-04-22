import "../scss/mercadopago.scss";

export default $(document).ready(e => {
    let $mpb = $(".mercadopago-button");
    $mpb.removeClass();
    $mpb.addClass("btn btn-primary");
    let $form = $("#payment-form.mercadopago");
    $form.removeClass("hidden");
});
