const express = require('express');
const paypal = require('@paypal/checkout-server-sdk');

const router = express.Router();

// PayPal SDK configuration
const paypalClient = () => {
  return new paypal.core.PayPalHttpClient(
    new paypal.core.SandboxEnvironment(
      process.env.PAYPAL_CLIENT_ID,
      process.env.PAYPAL_CLIENT_SECRET
    )
  );
};

// Create PayPal Order
router.post('/create-order', async (req, res) => {
  try {
    const { amount, currency = 'USD' } = req.body;

    const request = new paypal.orders.OrdersCreateRequest();
    request.requestBody({
      intent: 'CAPTURE',
      purchase_units: [{
        amount: {
          currency_code: currency,
          value: amount.toFixed(2)
        },
        description: 'Atlantiplex Studio Subscription',
        custom_id: req.user?.id || 'guest'
      }]
    });

    const client = paypalClient();
    const response = await client.execute(request);

    res.json({
      orderID: response.result.id,
      status: response.result.status
    });
  } catch (error) {
    console.error('PayPal order creation error:', error);
    res.status(500).json({ 
      error: 'Failed to create PayPal order',
      details: error.message 
    });
  }
});

// Capture PayPal Order
router.post('/capture-order', async (req, res) => {
  try {
    const { orderID } = req.body;

    const request = new paypal.orders.OrdersCaptureRequest(orderID);
    
    const client = paypalClient();
    const response = await client.execute(request);

    const captureData = response.result.purchase_units[0].payments.captures[0];
    
    if (response.result.status === 'COMPLETED') {
      // Record successful payment in database
      await recordSuccessfulPayment({
        provider: 'paypal',
        transactionId: captureData.id,
        orderId: orderID,
        amount: parseFloat(captureData.amount.value),
        currency: captureData.amount.currency_code,
        status: captureData.status,
        userId: req.user?.id || 'guest',
        metadata: {
          paypalOrder: response.result,
          captureDetails: captureData
        }
      });

      res.json({
        captured: true,
        transactionId: captureData.id,
        amount: captureData.amount.value,
        currency: captureData.amount.currency_code,
        status: captureData.status
      });
    } else {
      res.status(400).json({
        captured: false,
        error: 'Payment not completed',
        status: response.result.status
      });
    }
  } catch (error) {
    console.error('PayPal capture error:', error);
    res.status(500).json({ 
      error: 'Failed to capture PayPal payment',
      details: error.message 
    });
  }
});

// Get PayPal Order Details
router.get('/order/:orderID', async (req, res) => {
  try {
    const { orderID } = req.params;

    const request = new paypal.orders.OrdersGetRequest(orderID);
    const client = paypalClient();
    const response = await client.execute(request);

    res.json({
      order: response.result,
      status: response.result.status
    });
  } catch (error) {
    console.error('PayPal order details error:', error);
    res.status(500).json({ 
      error: 'Failed to get PayPal order details',
      details: error.message 
    });
  }
});

// Refund PayPal Payment
router.post('/refund', async (req, res) => {
  try {
    const { captureId, amount } = req.body;

    const request = new paypal.payments.CapturesRefundRequest(captureId);
    
    if (amount) {
      request.requestBody({
        amount: {
          value: amount.toFixed(2),
          currency_code: 'USD'
        }
      });
    }

    const client = paypalClient();
    const response = await client.execute(request);

    // Record refund in database
    await recordRefund({
      provider: 'paypal',
      refundId: response.result.id,
      captureId: captureId,
      amount: amount ? parseFloat(amount) : null,
      status: response.result.status,
      userId: req.user?.id || 'guest'
    });

    res.json({
      refunded: true,
      refundId: response.result.id,
      status: response.result.status
    });
  } catch (error) {
    console.error('PayPal refund error:', error);
    res.status(500).json({ 
      error: 'Failed to process PayPal refund',
      details: error.message 
    });
  }
});

// Get PayPal Transaction History
router.get('/transactions', async (req, res) => {
  try {
    const { startDate, endDate, pageSize = 20 } = req.query;

    let request = new paypal.payments.CapturesListRequest();
    
    if (startDate) {
      request = new paypal.payments.CapturesListRequest()
        .startDate(startDate)
        .endDate(endDate || new Date().toISOString());
    }

    request.pageSize(pageSize);

    const client = paypalClient();
    const response = await client.execute(request);

    res.json({
      transactions: response.result.captures,
      totalCount: response.result.total_items,
      hasMore: response.result.links.some(link => link.rel === 'next')
    });
  } catch (error) {
    console.error('PayPal transactions error:', error);
    res.status(500).json({ 
      error: 'Failed to get PayPal transactions',
      details: error.message 
    });
  }
});

// PayPal Webhook Handler
router.post('/webhook', async (req, res) => {
  try {
    const event = req.body;
    const webhookId = process.env.PAYPAL_WEBHOOK_ID;

    // Verify webhook signature
    const isValid = await verifyPayPalWebhook(req.headers, webhookId, req.body);
    
    if (!isValid) {
      return res.status(401).json({ error: 'Invalid webhook signature' });
    }

    // Handle different event types
    switch (event.event_type) {
      case 'PAYMENT.CAPTURE.COMPLETED':
        await handlePayPalPaymentCompleted(event);
        break;
      case 'PAYMENT.CAPTURE.DENIED':
        await handlePayPalPaymentDenied(event);
        break;
      case 'PAYMENT.CAPTURE.REFUNDED':
        await handlePayPalPaymentRefunded(event);
        break;
      default:
        console.log(`Unhandled PayPal webhook: ${event.event_type}`);
    }

    res.status(200).send('OK');
  } catch (error) {
    console.error('PayPal webhook error:', error);
    res.status(500).json({ 
      error: 'Webhook processing failed',
      details: error.message 
    });
  }
});

// Helper functions
async function recordSuccessfulPayment(paymentData) {
  // Implementation to record payment in database
  console.log('Recording PayPal payment:', paymentData);
  // Add your database logic here
}

async function recordRefund(refundData) {
  // Implementation to record refund in database
  console.log('Recording PayPal refund:', refundData);
  // Add your database logic here
}

async function verifyPayPalWebhook(headers, webhookId, body) {
  // Implementation to verify PayPal webhook signature
  // This is important for security
  const authAlgo = headers['paypal-auth-algo'];
  const transmission_id = headers['paypal-transmission-id'];
  const cert_id = headers['paypal-cert-id'];
  const transmission_sig = headers['paypal-transmission-sig'];
  const transmission_time = headers['paypal-transmission-time'];
  const actual_sign = headers['paypal-transmission-sig'];
  
  // Verify using PayPal SDK
  try {
    const client = paypalClient();
    const verifyRequest = new paypal.notifications.WebhooksVerifyRequest();
    verifyRequest.requestBody({
      auth_algo: authAlgo,
      cert_id: cert_id,
      transmission_id: transmission_id,
      transmission_sig: transmission_sig,
      transmission_time: transmission_time,
      webhook_id: webhookId,
      webhook_event: body
    });
    
    const response = await client.execute(verifyRequest);
    return response.result.verification_status === 'SUCCESS';
  } catch (error) {
    console.error('PayPal webhook verification failed:', error);
    return false;
  }
}

async function handlePayPalPaymentCompleted(event) {
  // Handle successful PayPal payment
  console.log('PayPal payment completed:', event);
  // Update user subscription, send confirmation, etc.
}

async function handlePayPalPaymentDenied(event) {
  // Handle denied PayPal payment
  console.log('PayPal payment denied:', event);
  // Notify user, update payment status, etc.
}

async function handlePayPalPaymentRefunded(event) {
  // Handle PayPal refund
  console.log('PayPal payment refunded:', event);
  // Update subscription, send refund confirmation, etc.
}

module.exports = router;