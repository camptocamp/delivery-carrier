# -*- coding: utf-8 -*-
@swisslux @setup @partner

Feature: Manage partner informations

  @csv @partner_category
  Scenario: import partner categories
    Given "res.partner.category" is imported from CSV "setup/res.partner.category.csv" using delimiter ","
 
