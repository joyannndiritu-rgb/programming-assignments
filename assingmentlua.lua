-- Global tables to track the final output categories
local summary = {
    completed = {},
    failed = {},
    cancelled = {}
}

-- The multi-stage pipeline steps
local STAGES = {
    "Validation", 
    "Payment Verification", 
    "Warehouse Allocation", 
    "Packaging", 
    "Courier Assignment", 
    "Dispatch"
}

-- Helper logic function that evaluates logistics constraints and PRINTS explicit decisions
local function processStageLogistics(orderState, stageName)
    
    -- 1. EXPLICIT M-PESA CHECK
    if stageName == "Payment Verification" then
        print(string.format("[EVALUATION] Checking: Does Wallet (%d KES) >= Item Price (%d KES)?", 
            orderState.mpesaBalance, orderState.price))
        
        if orderState.price > orderState.mpesaBalance then
            -- The mathematical reason for cancellation
            return "FAIL", string.format("CANCELLED because Item Cost (%d KES) is GREATER than M-Pesa Balance (%d KES). Shortage of %d KES.", 
                orderState.price, orderState.mpesaBalance, (orderState.price - orderState.mpesaBalance))
        else
            print(string.format("[APPROVED] Wallet has enough funds! Remaining balance will be %d KES.", 
                (orderState.mpesaBalance - orderState.price)))
        end
    end

    -- 2. EXPLICIT WAREHOUSE STOCK CHECK
    if stageName == "Warehouse Allocation" then
        print(string.format("[EVALUATION] Checking Inventory Database: Is '%s' available in stock? Status = %s", 
            orderState.item, tostring(orderState.inStock)))
        
        if orderState.inStock == false then
            -- How the computer knows it is out of stock
            return "FAIL", string.format("CANCELLED because internal database flag 'inStock' is set to FALSE for this item (%s).", 
                orderState.item)
        else
            print(string.format("[APPROVED] Inventory database confirms '%s' is present on shelves.", orderState.item))
        end
    end

    return "SUCCESS", "Passed"
end

-- function representing the life cycle of a single order
local function orderWorkflow(orderData)
    -- Persistent state stored safely inside this closure instance (marks a, b, c)
    local orderState = {
        id = orderData.id,
        customer = orderData.name,
        item = orderData.item,
        price = orderData.price,
        mpesaBalance = orderData.balance,
        inStock = orderData.inStock,
        currentStageIndex = 1
    }

    print(string.format("\n[Order %d] New Order Added: %s wants to buy [%s]", orderState.id, orderState.customer, orderState.item))

    -- Process stages step by step
    while orderState.currentStageIndex <= #STAGES do
        local stageName = STAGES[orderState.currentStageIndex]
        print(string.format("[Order %d] Shifting to Pipeline Stage -> %s", orderState.id, stageName))

        -- Execute the logistics logic checks
        local status, message = processStageLogistics(orderState, stageName)

        if status == "FAIL" then
            -- Stop execution immediately if an unrecoverable condition occurs
            return "CANCELLED", message
        end

        -- Move internal pointer state to the next stage index
        orderState.currentStageIndex = orderState.currentStageIndex + 1
        
        -- Pause the order here and hand control back to the scheduler
        coroutine.yield("RUNNING")
    end

    return "COMPLETED", string.format("Delivered %s to %s successfully.", orderState.item, orderState.customer)
end

-- Central Management System Scheduler Engine (marks d)
local function runCentralScheduler()
    -- Complete database of 5 hardcoded fictional Kenyan marketplace orders
    local ordersDatabase = {
        { id = 101, name = "Kamau Mwangi",     item = "Leather Shoes", price = 3500,  balance = 5000,  inStock = true },  
        { id = 102, name = "Amina Omondi",     item = "Smart Watch",   price = 12000, balance = 2500,  inStock = true },  -- Fails M-Pesa (12k > 2.5k)
        { id = 103, name = "John Otieno",      item = "Electric Kettle",price = 4500,  balance = 6000,  inStock = true },  
        { id = 104, name = "Faith Chepkorir",  item = "Subwoofer",     price = 8500,  balance = 10000, inStock = false }, -- Fails Stock (inStock = false)
        { id = 105, name = "Grace Mutua",      item = "Phone Charger", price = 1500,  balance = 3000,  inStock = true }   
    }

    -- Wrap each data package inside its own active coroutine thread object
    local activeQueue = {}
    for _, data in ipairs(ordersDatabase) do
        local co = coroutine.create(function()
            return orderWorkflow(data)
        end)
        
        table.insert(activeQueue, { id = data.id, coroutineObject = co })
    end

    print("\n=== STARTING SCHEDULER: INITIALIZING 5 INTERLEAVED ORDERS ===\n")

    -- Interleaved Loop Execution Controller
    while #activeQueue > 0 do
        local nextQueue = {}

        for _, task in ipairs(activeQueue) do
            local co = task.coroutineObject
            
            if coroutine.status(co) ~= "dead" then
                local success, executionState, message = coroutine.resume(co)

                if not success then
                    print(string.format("[SYSTEM CRASH] Order %d encountered a critical bug: %s", task.id, tostring(executionState)))
                else
                    if coroutine.status(co) == "dead" then
                        if executionState == "COMPLETED" then
                            print(string.format(">> [Order %d] SUCCESS: %s", task.id, message))
                            table.insert(summary.completed, string.format("Order %d (Dispatched Successfully)", task.id))
                        elseif executionState == "CANCELLED" then
                            print(string.format("❌ [Order %d] PIPELINE TERMINATION: %s", task.id, message))
                            table.insert(summary.cancelled, string.format("Order %d (%s)", task.id, message))
                        end
                    else
                        table.insert(nextQueue, task)
                    end
                end
            end
        end
        activeQueue = nextQueue
    end

    -- Compile and print out final summary reports (marks e)
    print("\n=== FINAL FULFILMENT SYSTEM SUMMARY ===")
    print("SUCCESSFULLY DISPATCHED:")
    for _, item in ipairs(summary.completed) do print("  " .. item) end

    print("\nCANCELLED PIPELINE ENTRIES:")
    for _, item in ipairs(summary.cancelled) do print("  " .. item) end
end

-- Trigger execution run
runCentralScheduler()
