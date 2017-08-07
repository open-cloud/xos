
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


"use strict";angular.module("xos.subscribers",["ngResource","ngCookies","ui.router","xos.helpers"]).config(["$stateProvider",function(s){s.state("user-list",{url:"/",template:"<subscribers-list></subscribers-list>"})}]).config(["$httpProvider",function(s){s.interceptors.push("NoHyperlinks")}]).directive("subscribersList",function(){return{restrict:"E",scope:{},bindToController:!0,controllerAs:"vm",templateUrl:"templates/subscribers-list.tpl.html",controller:function(){this.smartTableConfig={resource:"Subscribers"},this.model={label:{name:"aaa"},empty:{}},this.config={exclude:["password","last_login"],formName:"sampleForm",actions:[{label:"Save",icon:"ok",cb:function(s){console.log(s)},"class":"success"}]}}}}),angular.module("xos.subscribers").run(["$templateCache",function(s){s.put("templates/subscribers-list.tpl.html",'<!-- <xos-form ng-model="vm.model" config="vm.config"></xos-form> -->\n<xos-smart-table config="vm.smartTableConfig"></xos-smart-table>')}]),angular.module("xos.subscribers").run(["$location",function(s){s.path("/")}]);