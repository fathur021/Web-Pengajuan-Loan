-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 09, 2024 at 03:39 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pengajuanpinjaman`
--

-- --------------------------------------------------------

--
-- Table structure for table `completed_loans`
--

CREATE TABLE `completed_loans` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `Gender` int(11) DEFAULT NULL,
  `Married` int(11) DEFAULT NULL,
  `Dependents` int(11) DEFAULT NULL,
  `Education` int(11) DEFAULT NULL,
  `Self_Employed` int(11) DEFAULT NULL,
  `ApplicantIncome` float DEFAULT NULL,
  `CoapplicantIncome` float DEFAULT NULL,
  `LoanAmount` float DEFAULT NULL,
  `Loan_Amount_Term` float DEFAULT NULL,
  `Credit_History` int(11) DEFAULT NULL,
  `Property_Area` int(11) DEFAULT NULL,
  `loan_status` int(11) DEFAULT NULL,
  `completion_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `completed_loans`
--

INSERT INTO `completed_loans` (`id`, `user_id`, `Gender`, `Married`, `Dependents`, `Education`, `Self_Employed`, `ApplicantIncome`, `CoapplicantIncome`, `LoanAmount`, `Loan_Amount_Term`, `Credit_History`, `Property_Area`, `loan_status`, `completion_date`) VALUES
(10, 33, 0, 0, 0, 0, 0, 5000, 0, 100, 12, 1, 0, 1, '2024-06-08 23:55:51'),
(11, 33, 0, 0, 1, 0, 0, 5000, 3000, 120, 12, 1, 0, 1, '2024-06-09 00:08:29');

-- --------------------------------------------------------

--
-- Table structure for table `data_user`
--

CREATE TABLE `data_user` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `Gender` varchar(10) DEFAULT NULL,
  `Married` varchar(3) DEFAULT NULL,
  `Dependents` int(11) DEFAULT NULL,
  `Education` varchar(20) DEFAULT NULL,
  `Self_Employed` varchar(3) DEFAULT NULL,
  `ApplicantIncome` int(10) DEFAULT NULL,
  `CoapplicantIncome` int(10) DEFAULT NULL,
  `LoanAmount` int(10) DEFAULT NULL,
  `Loan_Amount_Term` int(11) DEFAULT NULL,
  `Credit_History` int(11) DEFAULT NULL,
  `Property_Area` varchar(20) DEFAULT NULL,
  `loan_status` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` tinyint(1) NOT NULL DEFAULT 0,
  `registration_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `verification_token` varchar(100) DEFAULT NULL,
  `verified` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password`, `role`, `registration_date`, `verification_token`, `verified`) VALUES
(31, 'fathur', 'fathur@gmail.com', '081231241', 'scrypt:32768:8:1$35KvhK1lvF3b1S1Z$d214a767cd675bcb608e2d88e61355668db0318f4c07bda8a080f47146f00df0e2e5c33429afa5821f9176df02d2a8efd265b13cbfb3481957d1076e7ae28d6f', 1, '2024-06-08 09:35:06', NULL, 0),
(33, 'ucup', 'ucup@gmail.com', '08123124', 'scrypt:32768:8:1$5BwUNkEOm1oKMXX1$224c40facb13fdf7a86e5455a65de450d85351f0f5ba2e4747a31718e2dde7041ebbcec64cd21b915b908ebda5a1b64fce4bb3447cd4502dcde0e7c0ed3a6eb6', 0, '2024-06-08 23:30:20', NULL, 0),
(34, 'admin', 'admin@lendfriend.co.id', '08123463123', 'scrypt:32768:8:1$tcaB1ICjhXqcEbEq$e0c29a1cebfd0e1dfeb6f47f8b31e76f857f94ce9503d047fa6adca6e206868d773d5e5e82311841746a5d82ca3d6b47c12d4ffae36a0c676a1063a7dea85333', 1, '2024-06-09 00:00:08', NULL, 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `completed_loans`
--
ALTER TABLE `completed_loans`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `data_user`
--
ALTER TABLE `data_user`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `completed_loans`
--
ALTER TABLE `completed_loans`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `data_user`
--
ALTER TABLE `data_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=74;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `data_user`
--
ALTER TABLE `data_user`
  ADD CONSTRAINT `data_user_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
