-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: db:3306
-- Generation Time: Dec 10, 2024 at 06:16 PM
-- Server version: 8.0.34
-- PHP Version: 8.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ia637`
--

-- --------------------------------------------------------

--
-- Table structure for table `hotel_reservations`
--

CREATE TABLE `hotel_reservations` (
  `res_id` int NOT NULL,
  `check_in_date` date NOT NULL,
  `check_out_date` date NOT NULL,
  `payment_method` varchar(20) NOT NULL,
  `payment_date` date NOT NULL,
  `amount` int NOT NULL,
  `points_gained` int NOT NULL,
  `uid` int NOT NULL,
  `room_id` int NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hotel_rewards_redeemed`
--

CREATE TABLE `hotel_rewards_redeemed` (
  `transaction_id` int NOT NULL,
  `reward_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `description` varchar(100) NOT NULL,
  `points_used` int NOT NULL,
  `redeem_date` date NOT NULL,
  `uid` int NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hotel_rooms`
--

CREATE TABLE `hotel_rooms` (
  `room_id` int NOT NULL,
  `room_num` int NOT NULL,
  `price` int NOT NULL,
  `status` varchar(25) NOT NULL,
  `room_type` varchar(25) DEFAULT NULL,
  `description` varchar(50) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hotel_users`
--

CREATE TABLE `hotel_users` (
  `uid` int NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `phone` varchar(10) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password` varchar(100) NOT NULL,
  `membership_type` varchar(25) DEFAULT NULL,
  `discount_rate` float DEFAULT NULL,
  `free_water` tinyint(1) DEFAULT NULL,
  `free_wifi` tinyint(1) DEFAULT NULL,
  `total_points_gained` int DEFAULT NULL,
  `total_points_used` int DEFAULT NULL,
  `points_available` int GENERATED ALWAYS AS ((`total_points_gained` - `total_points_used`)) STORED
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `hotel_reservations`
--
ALTER TABLE `hotel_reservations`
  ADD PRIMARY KEY (`res_id`);

--
-- Indexes for table `hotel_rewards_redeemed`
--
ALTER TABLE `hotel_rewards_redeemed`
  ADD PRIMARY KEY (`transaction_id`);

--
-- Indexes for table `hotel_rooms`
--
ALTER TABLE `hotel_rooms`
  ADD PRIMARY KEY (`room_id`);

--
-- Indexes for table `hotel_users`
--
ALTER TABLE `hotel_users`
  ADD PRIMARY KEY (`uid`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `hotel_reservations`
--
ALTER TABLE `hotel_reservations`
  MODIFY `res_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `hotel_rewards_redeemed`
--
ALTER TABLE `hotel_rewards_redeemed`
  MODIFY `transaction_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `hotel_rooms`
--
ALTER TABLE `hotel_rooms`
  MODIFY `room_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `hotel_users`
--
ALTER TABLE `hotel_users`
  MODIFY `uid` int NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
