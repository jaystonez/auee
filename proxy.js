/**
 * proxy.js
 *
 * Message structure proxy for BrowserGPT.
 *
 * This proxy intercepts and transforms messages between the webpage and React Native:
 * - Outgoing: BGPT_INVOKE_EXTENSION → BGPT_TO_RN
 * - Incoming: RN_TO_BGPT or BGPT_TO_RN → BGPT_FROM_EXTENSION
 *
 * The proxy is structure-focused and only transforms the message format without
 * analyzing or modifying the content values themselves.
 */

// Check if we're in a Node.js environment for testing
const IS_NODE = typeof window === "undefined";

// Set up globals for Node.js testing
if (IS_NODE) {
	global.window = {
		postMessage: function (message) {
			console.log("[Mock] window.postMessage called with:", message);
			return message;
		},
		addEventListener: function (event, listener) {
			console.log(`[Mock] Added event listener for: ${event}`);
		},
		removeEventListener: function (event, listener) {
			console.log(`[Mock] Removed event listener for: ${event}`);
		},
		dispatchEvent: function (event) {
			console.log("[Mock] Dispatched event:", event.data);
			return true;
		},
		setCurrentStateId: "test-state-123",
		ReactNativeWebView: {
			postMessage: function (message) {
				console.log("[Mock] ReactNativeWebView.postMessage called with:", message);
			},
		},
	};

	global.navigator = {
		userAgent: "Mozilla/5.0 ReactNativeWebView Mobile",
	};

	global.document = {
		referrer: "",
	};

	global.MessageEvent = class MessageEvent {
		constructor(type, init) {
			this.type = type;
			this.data = init.data;
			this.origin = init.origin || "mock-origin";
			this.source = init.source;
		}
		stopImmediatePropagation() {
			console.log("[Mock] Event propagation stopped");
		}
	};
}

// Store the original postMessage function
const originalPostMessage = window.postMessage;

/**
 * Detects if the current environment is React Native WebView
 * @returns {boolean} true if in React Native WebView
 */
function isPlatformReactNative() {
	if (typeof window.ReactNativeWebView !== "undefined") {
		console.log("[MessageProxy] Running in React Native WebView environment");
		return true;
	}

	// Check for userAgent patterns that might indicate React Native WebView
	const userAgent = navigator.userAgent.toLowerCase();
	if (
		userAgent.includes("reactnative") ||
		(userAgent.includes("android") && userAgent.includes("wv")) ||
		userAgent.includes("browsergpt-mobile")
	) {
		return true;
	}

	// Additional checks for specific mobile patterns with BrowserGPT
	if (
		userAgent.includes("mobile") &&
		(document.referrer.includes("browsergpt") || window.location.href.includes("browsergptapp"))
	) {
		return true;
	}

	return false;
}

window.isPlatformReactNative = isPlatformReactNative;

// Feature flag for enabling/disabling the proxy
let proxyEnabled = IS_NODE
	? true
	: typeof window.ENABLE_RN_MESSAGE_PROXY !== "undefined"
		? window.ENABLE_RN_MESSAGE_PROXY
		: true;

/**
 * Enable or disable the postMessage proxy
 * @param {boolean} enabled - true to enable, false to disable
 */
window.setMessageProxyEnabled = function (enabled) {
	proxyEnabled = enabled;
	if (typeof window.ENABLE_RN_MESSAGE_PROXY !== "undefined") {
		window.ENABLE_RN_MESSAGE_PROXY = enabled;
	}
	console.log(`[MessageProxy] ${enabled ? "Enabled" : "Disabled"}`);
};

/**
 * Override window.postMessage to intercept outgoing messages
 */
window.postMessage = function (message, targetOrigin, transfer) {
	// Skip transformation if proxy is disabled
	if (!proxyEnabled) {
		return originalPostMessage.call(window, message, targetOrigin, transfer);
	}

	try {
		// Only transform in React Native environment
		if (isPlatformReactNative() && typeof message === "object") {
			// Handle BGPT_INVOKE_EXTENSION → BGPT_TO_RN
			if (message.type === "BGPT_INVOKE_EXTENSION") {
				// Send original message for backward compatibility
				//originalPostMessage.call(window, message, targetOrigin, transfer);

				// Create BGPT_TO_RN format
				const rnMessage = transformToBGPTToRN(message);
				return originalPostMessage.call(window, rnMessage, targetOrigin, transfer);
			}
		}

		// Pass through all other messages unchanged
		return originalPostMessage.call(window, message, targetOrigin, transfer);
	} catch (error) {
		console.error("[MessageProxy] Error:", error);
		return originalPostMessage.call(window, message, targetOrigin, transfer);
	}
};

/**
 * Transform BGPT_INVOKE_EXTENSION message to BGPT_TO_RN format
 * @param {Object} message - Original BGPT_INVOKE_EXTENSION message
 * @returns {Object} - Transformed BGPT_TO_RN message
 */
function transformToBGPTToRN(message) {
	// Create basic BGPT_TO_RN structure
	const callbackId = `bgpt_callback_${message.instructionId || Date.now()}`;

	// Transform to Format 1 (with request object)
	const rnMessage = {
		type: "BGPT_TO_RN",
		callbackId: callbackId,
		request: {},
	};

	// Copy all properties from original message to request object
	// excluding 'type' which is set at the top level
	for (const [key, value] of Object.entries(message)) {
		if (key !== "type") {
			rnMessage.request[key] = value;
		}
	}

	// Rename keys to match React Native expectations
	if (rnMessage.request.apikey) {
		rnMessage.request.apiKey = rnMessage.request.apikey;
		delete rnMessage.request.apikey;
	}

	if (message.instructionId) {
		rnMessage.request.requestId = message.instructionId;
	}

	// Remove undefined properties
	Object.keys(rnMessage.request).forEach((key) => {
		if (rnMessage.request[key] === undefined) {
			delete rnMessage.request[key];
		}
	});

	return rnMessage;
}

/**
 * Transform RN_TO_BGPT message to BGPT_FROM_EXTENSION format
 * @param {Object} data - Message data from RN
 * @returns {Object} - Transformed BGPT_FROM_EXTENSION message
 */
function transformRNToBGPT(rnMessage) {
	if (!rnMessage || !rnMessage.request) {
		return null;
	}

	// Basic structure for BGPT_FROM_EXTENSION
	const bgptMessage = {
		type: "BGPT_FROM_EXTENSION",
		content: {
			...rnMessage.request,
			// Set default status if not provided
			status: rnMessage.request.status || "info_message",
			// Ensure message field exists
			message:
				rnMessage.request.message || rnMessage.request.result || rnMessage.request.text || "Action completed",
		},
	};

	// Handle different incoming message formats
	if (data.type === "RN_TO_BGPT" && data.request) {
		// Handle RN_TO_BGPT format
		extensionMessage.content = { ...data.request };

		// Set default status if not provided
		if (!extensionMessage.content.status) {
			extensionMessage.content.status = "info_message";
		}
	} else if (data.type === "BGPT_TO_RN" && data.response) {
		// Handle BGPT_TO_RN response format
		extensionMessage.content = { ...data.response };

		// Map aiAction to action if present
		if (data.response.aiAction && !data.response.action) {
			extensionMessage.content.action = data.response.aiAction;
		}

		// Set default status if not provided
		if (!extensionMessage.content.status) {
			extensionMessage.content.status =
				data.response.status === "error"
					? "failed_task"
					: data.response.status === "success"
						? "completed_task"
						: "info_message";
		}
	}

	// Copy stateId if available
	if (data.stateId) {
		extensionMessage.content.stateId = data.stateId;
	} else if (window.setCurrentStateId) {
		extensionMessage.content.stateId = window.setCurrentStateId;
	}

	// Ensure message field exists
	if (!extensionMessage.content.message) {
		extensionMessage.content.message =
			extensionMessage.content.result || extensionMessage.content.text || "Action completed";
	}

	return extensionMessage;
}

/**
 * Message listener to transform incoming messages from React Native
 */
const transformMessageListener = function (event) {
	if (!proxyEnabled || !isPlatformReactNative()) return;

	try {
		if (event.data && typeof event.data === "object") {
			// Check if this is from React Native and needs transformation
			if (event.data.type === "RN_TO_BGPT" && event.data.request) {
				// Transform to BGPT_FROM_EXTENSION format
				const bgptMessage = {
					type: "BGPT_FROM_EXTENSION",
					content: {
						...event.data.request,
						// Set default status if not provided
						status: event.data.request.status || "info_message",
						// Ensure message field exists
						message:
							event.data.request.message ||
							event.data.request.result ||
							event.data.request.text ||
							"Action completed",
					},
				};

				// Add stateId if available
				if (event.data.stateId) {
					bgptMessage.content.stateId = event.data.stateId;
				} else if (window.setCurrentStateId) {
					bgptMessage.content.stateId = window.setCurrentStateId;
				}

				// Create new message event
				const newEvent = new MessageEvent("message", {
					data: bgptMessage,
					origin: event.origin,
					source: event.source,
				});

				// Prevent recursion by temporarily removing listener
				window.removeEventListener("message", transformMessageListener, true);

				// Dispatch the transformed event
				window.dispatchEvent(newEvent);

				// Re-add the listener
				window.addEventListener("message", transformMessageListener, true);

				// Prevent original event propagation
				event.stopImmediatePropagation();
			}
		}
	} catch (error) {
		console.error("[MessageProxy] Error in message transformer:", error);
	}
};

// Add message listener with capture phase to intercept before other listeners
window.addEventListener("message", transformMessageListener, true);

// Setup initialization to ensure proxy is ready early
function initMessageProxy() {
	// Check for environment
	const isRN = isPlatformReactNative();

	console.log(`[MessageProxy] Initialized in ${isRN ? "React Native" : "browser"} environment`);
	console.log(`[MessageProxy] Proxy is currently ${proxyEnabled ? "enabled" : "disabled"}`);

	// Set a global variable to indicate RN detection
	window.IS_REACT_NATIVE_WEBVIEW = isRN;

	if (isRN) {
		// Additional RN-specific setup if needed
		console.log("[MessageProxy] Setting up React Native specific handlers");

		// Notify React Native that the proxy is ready
		if (window.ReactNativeWebView && typeof window.ReactNativeWebView.postMessage === "function") {
			window.ReactNativeWebView.postMessage(
				JSON.stringify({
					type: "PROXY_INITIALIZED",
					status: "ready",
				}),
			);
		}
	}
}

// Initialize the proxy
initMessageProxy();

console.log("[MessageProxy] Loaded successfully");

// Test mode - only run if NODE_ENV is test or if TEST_PROXY is set to true
if (
	(typeof process !== "undefined" && process.env.NODE_ENV === "test") ||
	(typeof window !== "undefined" && window.TEST_PROXY === true)
) {
	console.log("[MessageProxy] Running in test mode");

	// Mock environment for testing if needed
	if (typeof window === "undefined") {
		global.window = {
			postMessage: originalPostMessage,
			addEventListener: function () {},
			removeEventListener: function () {},
			dispatchEvent: function () {},
			setCurrentStateId: "test-state-123",
		};
	}

	// Ensure we're in "React Native" mode for testing
	window.ReactNativeWebView = window.ReactNativeWebView || {
		postMessage: function (msg) {
			console.log("[Test] ReactNativeWebView.postMessage:", msg);
		},
	};

	// Store original console.log
	const originalConsoleLog = console.log;

	// Set up logs that are easier to read in test output
	console.log = function (...args) {
		if (args[0] && typeof args[0] === "string" && args[0].startsWith("[Test]")) {
			originalConsoleLog("\x1b[33m%s\x1b[0m", ...args); // Yellow for test logs
		} else {
			originalConsoleLog(...args);
		}
	};

	// Test function to run all the test cases
	function runProxyTests() {
		console.log("[Test] ==============================================");
		console.log("[Test] Starting proxy transformation tests");
		console.log("[Test] ==============================================");

		// Test 1: BGPT_INVOKE_EXTENSION → BGPT_TO_RN (Simple message)
		console.log("\n[Test] Test 1: BGPT_INVOKE_EXTENSION → BGPT_TO_RN (Simple)");

		const extensionMessage = {
			type: "BGPT_INVOKE_EXTENSION",
			action: "captureScreen",
			apikey: "user_license_key",
			currentStateId: "current_state_id",
			bgptIndex: false,
			instructionId: "instr_123456",
		};

		console.log("[Test] Input:", JSON.stringify(extensionMessage, null, 2));
		const transformedMessage1 = transformToBGPTToRN(extensionMessage);
		console.log("[Test] Output:", JSON.stringify(transformedMessage1, null, 2));

		// Test 2: BGPT_INVOKE_EXTENSION → BGPT_TO_RN (Complex message)
		console.log("\n[Test] Test 2: BGPT_INVOKE_EXTENSION → BGPT_TO_RN (Complex)");

		const taskExecutionMessage = {
			type: "BGPT_INVOKE_EXTENSION",
			action: "captureTab",
			prompt: "user_prompt",
			data: {
				status: "success",
				action: "task_list",
				tasks: [],
				summary: "",
				reasoning: "",
				prompt: "user_prompt",
				referenced_patterns: {},
			},
			apikey: "user_license_key",
			bgptIndex: false,
			currentStateId: "current_state_id",
			instructionId: "instruction_id",
			enable_realtime_mode: false,
			directExecution: false,
		};

		console.log("[Test] Input:", JSON.stringify(taskExecutionMessage, null, 2));
		const transformedMessage2 = transformToBGPTToRN(taskExecutionMessage);
		console.log("[Test] Output:", JSON.stringify(transformedMessage2, null, 2));

		// Test 3: RN_TO_BGPT → BGPT_FROM_EXTENSION (DOM action)
		console.log("\n[Test] Test 3: RN_TO_BGPT → BGPT_FROM_EXTENSION (DOM action)");

		const rnToBgptMessage = {
			type: "RN_TO_BGPT",
			callbackId: "callback_123",
			request: {
				action: "CLICK",
				selector: "#submit-button",
				text: null,
				requestId: "req_123456",
			},
		};

		// Create mock event
		const mockEvent1 = {
			data: rnToBgptMessage,
			source: window,
			stopImmediatePropagation: function () {
				console.log("[Test] Event propagation stopped");
			},
		};

		// Capture the transformed message by mocking dispatchEvent
		let capturedEvent1 = null;
		const originalDispatchEvent = window.dispatchEvent;
		window.dispatchEvent = function (event) {
			capturedEvent1 = event;
			console.log("[Test] Event dispatched");
			return true;
		};

		console.log("[Test] Input:", JSON.stringify(mockEvent1.data, null, 2));

		// Use direct function call to avoid issues with the listener removal/re-adding
		const transformResult = directTransform(mockEvent1);
		if (transformResult) {
			console.log("[Test] Output:", JSON.stringify(capturedEvent1.data, null, 2));
		} else {
			console.log("[Test] Transformation failed or no message was dispatched");
		}

		// Test 4: RN_TO_BGPT → BGPT_FROM_EXTENSION (Navigation)
		console.log("\n[Test] Test 4: RN_TO_BGPT → BGPT_FROM_EXTENSION (Navigation)");

		const navigationMessage = {
			type: "RN_TO_BGPT",
			callbackId: "callback_456",
			request: {
				action: "NAVIGATE",
				url: "https://example.com",
				status: "success",
				requestId: "req_456789",
			},
		};

		// Create mock event
		const mockEvent2 = {
			data: navigationMessage,
			source: window,
			stopImmediatePropagation: function () {
				console.log("[Test] Event propagation stopped");
			},
		};

		// Reset captured event
		capturedEvent1 = null;

		console.log("[Test] Input:", JSON.stringify(mockEvent2.data, null, 2));

		// Use direct function call again
		const transformResult2 = directTransform(mockEvent2);
		if (transformResult2) {
			console.log("[Test] Output:", JSON.stringify(capturedEvent1.data, null, 2));
		} else {
			console.log("[Test] Transformation failed or no message was dispatched");
		}

		// Restore original dispatchEvent
		window.dispatchEvent = originalDispatchEvent;

		console.log("\n[Test] ==============================================");
		console.log("[Test] All tests completed");
		console.log("[Test] ==============================================");
	}

	// Helper function to directly transform a message without using the actual event listener
	function directTransform(event) {
		if (event.data && typeof event.data === "object") {
			// Check if this is from React Native and needs transformation
			if (event.data.type === "RN_TO_BGPT" && event.data.request) {
				// Transform to BGPT_FROM_EXTENSION format
				const bgptMessage = {
					type: "BGPT_FROM_EXTENSION",
					content: {
						...event.data.request,
						// Set default status if not provided
						status: event.data.request.status || "info_message",
						// Ensure message field exists
						message:
							event.data.request.message ||
							event.data.request.result ||
							event.data.request.text ||
							"Action completed",
					},
				};

				// Add stateId if available
				if (event.data.stateId) {
					bgptMessage.content.stateId = event.data.stateId;
				} else if (window.setCurrentStateId) {
					bgptMessage.content.stateId = window.setCurrentStateId;
				}

				// Create new message event
				const newEvent = new MessageEvent("message", {
					data: bgptMessage,
					origin: "test-origin",
					source: window,
				});

				// Dispatch the event
				window.dispatchEvent(newEvent);
				return true;
			}
		}
		return false;
	}

	// If this is being run directly with Node.js, execute the tests
	if (typeof process !== "undefined" && typeof require !== "undefined") {
		// Set up minimal MessageEvent if not available
		if (typeof MessageEvent === "undefined") {
			global.MessageEvent = class MockMessageEvent {
				constructor(type, init) {
					this.type = type;
					this.data = init.data;
					this.origin = init.origin;
					this.source = init.source;
				}
			};
		}

		// Make setTimeout available if needed
		if (typeof setTimeout === "undefined") {
			global.setTimeout = function (fn) {
				fn();
			};
		}

		// Run the tests
		runProxyTests();
	} else {
		// In browser, make test function available on window
		window.runProxyTests = runProxyTests;
		console.log("[MessageProxy] Test mode enabled. Run tests with window.runProxyTests()");
	}
}
