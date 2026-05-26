-- 05_sample_data.sql
-- Insertion de quelques transactions factices pour tester l'API et les Vues

INSERT INTO fraud_detection.transactions 
(transaction_id, transaction_time, V1, V2, amount, is_fraud, confidence_score)
VALUES 
('TXN-TEST-001', 0.0, -1.3598, -0.0727, 149.62, FALSE, 0.98),
('TXN-TEST-002', 1.0, 1.1918, 0.2661, 2.69, FALSE, 0.99),
('TXN-TEST-003', 406.0, -2.3122, 1.9519, 0.00, TRUE, 0.94); -- Transaction frauduleuse simulée