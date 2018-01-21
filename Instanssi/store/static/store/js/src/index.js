/* global $ */

// IE11 support
import 'core-js/es6/array';
import 'core-js/es6/object';
import 'core-js/es6/promise';

import Vue from 'vue';

import {
    formatPrice,
    storeXHR,
    loadingOverlay,
    cartItemEquals,
} from './store_common.js';

import './store_information.js';
import './store_cart.js';
import './store_product.js';

const PAYMENT_METHODS = [
    { id: 1, name: 'Paytrail verkkomaksu' },
    { id: 0, name: 'BitPay (maksa BitCoinilla)' },
];

const NO_PAYMENT_METHODS = [
    // This is offered if and only if a non-empty cart's total is 0.
    { id: -1, name: 'Ei maksua' },
];

/**
 * Fetch items from the store API.
 * @returns {Promise.<Object>} - API response
 */
function fetchItems() {
    return storeXHR('GET', '/api/v1/store_items/?format=json');
}
/**
 * Submits a transaction to the store API.
 * @param {Object} transaction - Transaction data
 * @returns {Promise.<Object>} - API response
 */
function submitTransaction(transaction) {
    return storeXHR('POST', '/api/v1/store_transaction/?format=json', transaction);
}

function scrollToTop() {
    $('html,body').animate({
        scrollTop: $(".store").offset().top
    }, 500);
}

Vue.filter('formatPrice', formatPrice);


/**
 * Instanssi.org store frontend application.
 */
const app = new Vue({
    el: '#store',
    data: {
        /** Current step. 0 = products, 1 = info, 2 = summary & payment */
        step: 0,
        /** Products list. */
        products: [],
        /** Current shopping cart contents. */
        cart: [],
        /** Form messages, as Object of field names to Array.<String>. */
        messages: {},
        /** Set to 'done' or 'error' based on XHR result. */
        loadingStatus: 'loading',
        /** Customer information for payment and delivery purposes. */
        info: {
            first_name: '',
            last_name: '',
            email: '',
            email2: '',
            street: '',
            postal_code: '',
            city: '',
            country: 'fi',
            mobile: '',
            telephone: '',
            company: '',
            information: '',
            read_terms: false,
        },
        /** Payment method, see PAYMENT_METHODS; default is Paytrail. */
        paymentMethod: 1,
        /** Current sum of cart item prices. */
        // totalPrice: 0,
        /** True if the customer info has been validated and has not changed since then. */
        customerInfoIsValid: false,
        /** Set when purchase is ready to be paid. */
        paymentURL: null,
        /** Set when transaction is being submitted (prevent accidental spam) */
        submitting: false,
    },
    template: require('./store.html'),
    created() {
        // fetch products list
        fetchItems().then((items) => {
            items.forEach((item) => {
                item.price = parseFloat(item.price);
            });
            this.products = items;
            this.loadingStatus = 'done';
        }).catch((e) => {
            console.error('error fetching store items:', e);
            this.loadingStatus = 'error';
        });

        // FIXME: Fetch cart from window.localstorage if it exists
    },
    computed: {
        paymentMethods() {
            if(this.totalPrice <= 0) {
                return NO_PAYMENT_METHODS;
            }
            return PAYMENT_METHODS;
        },
        totalPrice() {
            let totalPrice = 0;
            this.cart.forEach((cartItem) => {
                totalPrice += this.getSubtotal(cartItem);
            });
            return totalPrice;
        },
    },
    methods: {
        canMoveToStep(step) {
            // Not going anywhere if the payment URL is already set
            // or the UI is waiting for it.
            if(this.paymentURL !== null || this.submitting) {
                return step === 2;
            }
            let ok = true;
            if(step > 0) {
                ok = ok && this.cart.length > 0;
            }
            if(step > 1) {
                // Should we require that the user clicks the button at the bottom?
                // After that the customer info should be valid.
                // (disable the button again if the user changes their personal information)
                ok = ok && this.customerInfoIsValid;
            }
            return ok;
        },
        /**
         * Move between stages in the shopping process. May perform some validation.
         * @param {number} next - Next step to move to
         * @param {boolean} scrollUp - Should the page scroll up on successful transition?
         */
        toStep(next, scrollUp) {
            // you're not going anywhere if the payment URL is already set
            if(this.paymentURL !== null) {
                return;
            }
            // Check form status between steps so the user doesn't have to come back later.
            if(this.step === 0) {
                // 0 -> _: check that cart contains one item
                if(this.cart.length < 1) {
                    this.messages = {
                        items: [ 'Valitse ainakin yksi tuote.' ]
                    }
                    return;
                }
                this.messages = {};
                this.step = next;

                if(scrollUp) {
                    scrollToTop();
                }
            } else if (this.step === 1 && next === 2) {
                const { info } = this;
                // 1 -> 2: send a "save=false" transaction request

                // validate email before doing anything
                if(info.email !== info.email2) {
                    this.messages = {
                        email: ['Kirjoita sama sähköpostiosoite kahdesti.'],
                        email2: ['Kirjoita sama sähköpostiosoite kahdesti.']
                    };
                    return;
                }

                // validate what the user has input so far
                let transaction = this.getTransactionObject();
                // dry run only, don't actually try to complete the transaction
                transaction.save = false;

                submitTransaction(transaction).then((res) => {
                    this.messages = {};
                    this.step = next;
                    this.customerInfoIsValid = true;

                    if(scrollUp) {
                        scrollToTop();
                    }
                }).catch((err) => {
                    this.messages = err;
                });
            } else {
                // sure, whatever
                this.messages = {};
                this.step = next;

                if(scrollUp) {
                    scrollToTop();
                }
            }
        },
        /**
         * Pick up changes to the customer information.
         */
        updateInfo() {
            // require user to click the "next step" button again
            this.customerInfoIsValid = false;
        },
        /**
         * Calculates subtotal for a specific cart item, considering discounts, etc.
         * @param {Object} cartItem - Existing cart item
         * @return {number} - Subtotal for the item and its count in the cart
         */
        getSubtotal(cartItem) {
            let multiplier = 1;
            let qtyThresh = cartItem.product.discount_amount;
            let discountFactor = (100 - cartItem.product.discount_percentage) / 100;
            if(qtyThresh && cartItem.count >= qtyThresh) {
                multiplier *= discountFactor;
            }
            return cartItem.product.price * cartItem.count * multiplier;
        },
        /**
         * Update cart state, calculating total price and so on.
         */
        updateCart() {
            const { totalPrice } = this;
            if(totalPrice <= 0) {
                // Set payment method to "no payment" if total price is 0.
                this.paymentMethod = -1;
            } else if(this.paymentMethod === -1 && totalPrice > 0) {
                // Change it back if the price changes.
                this.paymentMethod = 1;
            }
        },
        /**
         * Add an item to the cart.
         * @param {Object} product - Product / StoreItem to add
         * @param {Object} [variant] - Variant to add, if any
         */
        addItem(product, variant) {
            if(this.paymentURL !== null) {
                return;
            }
            // check if product/variant is already in items
            let found = this.cart.findIndex((item) => {
                return cartItemEquals(item, product, variant);
            });
            if (found >= 0) {
                let cartItem = this.cart[found];
                this.changeItemCount(cartItem, 1);
            } else if (product.num_available > 0) {
                // if it isn't, push a new item
                this.cart.push({
                    count: 1,
                    product: product,
                    variant: variant
                });
                this.updateCart();
            }
        },
        /**
         * Removes one item from the cart.
         * @param {Object} product - Product / StoreItem to remove
         * @param {Object} [variant] - Variant to remove, if any
         */
        removeItem(product, variant) {
            if(this.paymentURL !== null) {
                return;
            }
            let found = this.cart.findIndex((item) => {
                return cartItemEquals(item, product, variant);
            });
            if(found >= 0) {
                this.changeItemCount(this.cart[found], -1);
            }
        },
        /**
         * Removes an existing cart item from the cart.
         * @param {Object} cartItem - Cart entry to remove
         */
        removeItemFromCart(cartItem) {
            if(this.paymentURL !== null) {
                return;
            }
            let pos = this.cart.indexOf(cartItem);
            this.cart.splice(pos, 1);
            this.updateCart();
        },
        /**
         * Updates an item's count in the shopping cart.
         * @param {Object} item - Product to update, must already exist in cart
         * @param {number} change - Items to add (or remove)
         */
        changeItemCount(item, change) {
            if(this.paymentURL !== null) {
                return;
            }
            let pos = this.cart.indexOf(item);
            let cartItem = this.cart[pos];
            let newCount = cartItem.count + change;
            if(newCount > cartItem.product.num_available) {
                newCount = cartItem.product.num_available;
            }
            // backend may set num_available = min(max_per_order, available - sold), let's make sure
            if(newCount > cartItem.product.max_per_order) {
                newCount = cartItem.product.max_per_order;
            }
            if (newCount <= 0) {
                this.removeItemFromCart(cartItem);
                return;
            }
            cartItem.count = newCount;
            this.cart.splice(pos, 1, cartItem);
            this.updateCart();
        },
        /**
         * Generates an API transaction object from the store's current state.
         * @returns {Object} - Transaction to submit
         */
        getTransactionObject() {
            let transaction = Object.assign({}, this.info);
            transaction.items = this.cart.map((item) => ({
                item_id: item.product.id,
                variant_id: item.variant ? item.variant.id : null,
                amount: item.count,
            }));
            transaction.payment_method = this.paymentMethod;
            return transaction;
        },
        /**
         * Sends the current store data to the backend.
         * @returns {Promise} - Request results
         */
        submit() {
            // Don't allow multiple transactions to be sent
            if(this.paymentURL !== null || this.submitting) {
                return;
            }
            let { info } = this;

            let transaction = this.getTransactionObject();
            transaction.save = true;

            // prevent multiple submits
            this.submitting = true;

            return submitTransaction(transaction).then((res) => {
                console.info(res);
                this.submitting = false;
                this.paymentURL = res.url;
                window.location.replace(this.paymentURL);
            }, (err) => {
                this.messages = err;
                this.submitting = false;
                // Manipulate error message so both email fields show errors
                if(err) {
                    err.email2 = err.email;
                }
            }).catch(err => {
                console.error(err);
            });
        }
    }
});
