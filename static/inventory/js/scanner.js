// sherlock-python/static/inventory/js/scanner.js

document.addEventListener('DOMContentLoaded', function () {
    // --- Universal Elements for the Scanner Modal ---
    const modal = document.getElementById('scanner-modal');
    const closeButton = document.querySelector('.scanner-close-button');
    const qrReaderElement = document.getElementById('qr-reader');

    if (!modal || !closeButton || !qrReaderElement) {
        // If the modal isn't on the page, don't run any scanner code.
        return;
    }

    // A single, shared scanner object. We initialize it the first time we need it.
    let html5QrcodeScanner;

    // A single function to safely stop the scanner and close the modal
    const stopScannerAndCloseModal = () => {
        if (html5QrcodeScanner && html5QrcodeScanner.getState() === Html5QrcodeScannerState.SCANNING) {
            html5QrcodeScanner.clear().catch(error => {
                // This can sometimes throw an error if it's already clearing, so we just log it.
                console.error("Error while clearing the scanner:", error);
            });
        }
        modal.style.display = "none";
    };

    // --- Event Listeners to Close the Modal ---
    closeButton.addEventListener('click', stopScannerAndCloseModal);
    window.addEventListener('click', (event) => {
        if (event.target == modal) {
            stopScannerAndCloseModal();
        }
    });

    // ====================================================================
    //  LOGIC FOR THE CHECKOUT TERMINAL SCANNER
    // ====================================================================
    const checkoutScanButton = document.getElementById('scan-item-button');
    const scannerForm = document.getElementById('scanner-form');
    const scannerBarcodeHiddenInput = document.getElementById('scanner-barcode-input');
    
    if (checkoutScanButton && scannerForm && scannerBarcodeHiddenInput) {
        
        const onCheckoutScanSuccess = (decodedText, decodedResult) => {
            console.log(`Checkout scan successful: ${decodedText}`);
            stopScannerAndCloseModal();
            scannerBarcodeHiddenInput.value = decodedText;
            scannerForm.requestSubmit();
        };

        checkoutScanButton.addEventListener('click', () => {
            modal.style.display = "block";
            if (!html5QrcodeScanner) {
                html5QrcodeScanner = new Html5QrcodeScanner("qr-reader", { fps: 10, qrbox: { width: 250, height: 250 } });
            }
            html5QrcodeScanner.render(onCheckoutScanSuccess, (error) => {}); // Start scanning
        });
    }

    // ====================================================================
    //  LOGIC FOR THE UNIVERSAL LOOKUP SCANNER
    // ====================================================================
    const universalScanButton = document.getElementById('universal-scan-button');
    const searchPageScanButton = document.getElementById('search-page-scan-button');
    
    const onUniversalScanSuccess = (decodedText, decodedResult) => {
        console.log(`Universal scan successful: ${decodedText}`);
        stopScannerAndCloseModal();
        
        // Construct the lookup URL and redirect the browser
        const lookupUrl = `/lookup/?code=${encodeURIComponent(decodedText)}`;
        window.location.href = lookupUrl;
    };

    const startUniversalScanner = () => {
        modal.style.display = "block";
        if (!html5QrcodeScanner) {
            html5QrcodeScanner = new Html5QrcodeScanner("qr-reader", { fps: 10, qrbox: { width: 250, height: 250 } });
        }
        html5QrcodeScanner.render(onUniversalScanSuccess, (error) => {}); // Start scanning
    };

    if (universalScanButton) {
        universalScanButton.addEventListener('click', startUniversalScanner);
    }
    if (searchPageScanButton) {
        searchPageScanButton.addEventListener('click', startUniversalScanner);
    }
});