%global pecl_name  imagick
%global php_base php56u
%global ini_name  40-%{pecl_name}.ini

# zts support copied/influenced from Remi Collet
# https://github.com/remicollet/remirepo/blob/master/php/pecl/php-pecl-imagick/php-pecl-imagick.spec
%global with_zts 0%{?__ztsphp:1}

Summary: Provides a wrapper to the ImageMagick library
Name: %{php_base}-pecl-%{pecl_name}
Version: 3.4.3
Release: 1.ius%{?dist}
License: PHP
Group: Development/Libraries
Source0: http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
Source1: %{pecl_name}.ini
URL: http://pecl.php.net/package/%{pecl_name}
BuildRequires: %{php_base}-pear
BuildRequires: %{php_base}-devel
# https://pecl.php.net/package-info.php?package=imagick&version=3.4.0RC2
BuildRequires: ImageMagick-devel >= 6.5.3.10
Requires(post): %{php_base}-pear
Requires(postun): %{php_base}-pear
Requires: %{php_base}(api) = %{php_core_api}
Requires: %{php_base}(zend-abi) = %{php_zend_api}

# provide the stock name
Provides: php-pecl-%{pecl_name} = %{version}
Provides: php-pecl-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides: php-%{pecl_name} = %{version}
Provides: php-%{pecl_name}%{?_isa} = %{version}
Provides: %{php_base}-%{pecl_name} = %{version}
Provides: %{php_base}-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides: php-pecl(%{pecl_name}) = %{version}
Provides: php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides: %{php_base}-pecl(%{pecl_name}) = %{version}
Provides: %{php_base}-pecl(%{pecl_name})%{?_isa} = %{version}

# conflict with the stock name
Conflicts: php-pecl-%{pecl_name} < %{version}

# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_provides_in: %filter_provides_in %{php_ztsextdir}/.*\.so$}
%{?filter_setup}


%description
%{pecl_name} is a native php extension to create and modify images using the
ImageMagick API. This extension requires ImageMagick version 6.2.4+ and
PHP 5.1.3+.

IMPORTANT: Version 2.x API is not compatible with earlier versions.


%prep
%setup -q -c

mv %{pecl_name}-%{version} NTS

%if %{with_zts}
cp -r NTS ZTS
%endif


%build
pushd NTS
phpize
%configure --with-imagick=%{prefix} --with-php-config=%{_bindir}/php-config
%{__make}
popd

%if %{with_zts}
pushd ZTS
zts-phpize
%configure --with-imagick=%{prefix} --with-php-config=%{_bindir}/zts-php-config
%{__make}
popd
%endif


%install
%{__make} install INSTALL_ROOT=%{buildroot} -C NTS

# Install XML package description
install -Dpm 0644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

# Install config file
install -Dpm 0644 %{SOURCE1} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with_zts}
%{__make} install INSTALL_ROOT=%{buildroot} -C ZTS

# Install config file
install -Dpm 0644 %{SOURCE1} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

rm -rf %{buildroot}%{php_incldir}/ext/%{pecl_name}/
%if %{with_zts}
rm -rf %{buildroot}%{php_ztsincldir}/ext/%{pecl_name}/
%endif


%check
# simple module load test
php --no-php-ini \
    --define extension_dir=%{buildroot}%{php_extdir} \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}
%if %{with_zts}
zts-php --no-php-ini \
    --define extension_dir=%{buildroot}%{php_ztsextdir} \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}
%endif


%post
%if 0%{?pecl_install:1}
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml
%endif


%postun
%if 0%{?pecl_uninstall:1}
if [ "$1" -eq "0" ]; then
  %{pecl_uninstall} %{pecl_name}
fi
%endif


%files
%doc NTS/examples NTS/CREDITS
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{pecl_name}.xml
%config(noreplace) %verify(not md5 mtime size) %{php_inidir}/%{ini_name}

%if %{with_zts}
%{php_ztsextdir}/%{pecl_name}.so
%config(noreplace) %verify(not md5 mtime size) %{php_ztsinidir}/%{ini_name}
%endif


%changelog
* Thu Feb 02 2017 Ben Harper <ben.harper@rackspace.com> - 3.4.3-1.ius
- Latest upstream

* Thu Jun 16 2016 Ben Harper <ben.harper@rackspace.com> - 3.4.1-2.ius
- update filters to include zts

* Tue Mar 15 2016 Carl George <carl.george@rackspace.com> - 3.4.1-1.ius
- Latest upstream
- ZTS cleanup
- Clean up provides
- Clean up filters
- Use standard PHP macros

* Wed Feb 17 2016 Carl George <carl.george@rackspace.com> - 3.3.0-3.ius
- Explicitly require %%{php_base}(api) and %%{php_base}(zend-abi)
- Manually filter provides only when needed

* Thu Jan 14 2016 Ben Harper <ben.harper@rackspace.com> - 3.3.0-2.ius
- enabled zts support, changes copied/influenced from Remi Collet
  https://github.com/remicollet/remirepo/blob/master/php/pecl/php-pecl-imagick/php-pecl-imagick.spec

* Mon Dec 07 2015 Ben Harper <ben.harper@rackspace.com> - 3.3.0-1.ius
- Latest sources from upstream
- remove TODO and INSTALL from %%files

* Tue Jul 28 2015 Ben Harper <ben.harper@rackspace.com> - 3.1.2-6.ius
- rebuild for updated ImageMagick in EL 6.7

* Mon Oct 27 2014 Ben Harper <ben.harper@rackspace.com> - 3.1.2-5.ius
- porting from php55u-pecl-imagick

* Fri Oct 10 2014 Carl George <carl.george@rackspace.com> - 3.1.2-4.ius
- Directly require the correct pear package, not /usr/bin/pecl
- Conflict with stock package
- Use same provides as stock package

* Fri Oct 03 2014 Carl George <carl.george@rackspace.com> - 3.1.2-3.ius
- Add numerical prefix to extension configuration file
- Add filter to avoid private-shared-object-provides
- Add minimal %%check
- Remove unneeded header files

* Thu Apr 10 2014 Ben Harper <ben.harper@rackspace.com> - 3.1.2-2.ius
- porting from php54-pecl-imagick

* Wed Sep 25 2013 Ben Harper <ben.harper@rackspace.com> - 3.1.2-1.ius
- Latest sources from upstream

* Mon Sep 23 2013 Ben Harper <ben.harper@rackspace.com> - 3.1.1-1.ius
- latest release, 3.1.1

* Tue Aug 21 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> - 3.1.0-RC1.2.ius
- Rebuilding against php54-5.4.6-2.ius as it is now using bundled PCRE.

* Fri May 11 2012 Dustin Henry Offutt <dustin.offutt@rackspace.com> 3.1.0-RC1.1.ius
- Building for php54 and imagick 3.1.0RC1
- Add define rc_version, add rc_version to Release definition, Source0 path, BuildRoot path, and setup line

* Fri Aug 19 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 3.0.1-3.ius
- Rebuilding

* Tue Feb 01 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 3.0.1-2.ius
- Removed Obsoletes: php53*

* Thu Dec 16 2010 BJ Dierkes <wdierkes@rackspace.com> - 3.0.1-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=imagick&release=3.0.1
- Renaming package as php53u-pecl-imagick, Resolves LP#691755
- Rebuild against php53u-5.3.4
- BuildRequires: php53u-cli

* Tue Jul 27 2010 BJ Dierkes <wdierkes@rackspace.com> - 3.0.0-1.ius
- Latest sources from upstream
- Porting over to php53 (5.3.3) 

* Thu Dec 17 2009 BJ Dierkes <wdierkes@rackspace.com> - 2.3.0-1.ius
- Rebuilding for IUS Community Project
- Latest sources from upstream
- Building against php52-5.2.12, php52-pear

* Sun Jan 11 2009 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] spb [ dOt.] su> - 2.2.1-3
- All modifications in this release inspired by Fedora review by Remi Collet.
- Add versions to BR for php-devel and ImageMagick-devel
- Remove -n option from %%setup which was excessive with -c
- Module install/uninstall actions surround with %%if 0%{?pecl_(un)?install:1} ... %%endif
- Add Provides: php-pecl(%%peclName) = %%{version}

* Sat Jan 3 2009 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] spb [ dOt.] su> - 2.2.1-2
- License changed to PHP (thanks to Remi Collet)
- Add -c flag to %%setup (Remi Collet)
  And accordingly it "cd %%peclName-%%{version}" in %%build and %%install steps.
- Add (from php-pear template)
  Requires(post): %%{__pecl}
  Requires(postun): %%{__pecl}
- Borrow from Remi Collet php-api/abi requirements.
- Use macroses: (Remi Collet)
  %%pecl_install instead of direct "pear install --soft --nobuild --register-only"
  %%pecl_uninstall instead of pear "uninstall --nodeps --ignore-errors --register-only"
- %%doc examples/{polygon.php,captcha.php,thumbnail.php,watermark.php} replaced by %%doc examples (Remi Collet)
- Change few patchs to macroses: (Remi Collet)
  %%{_libdir}/php/modules - replaced by %%{php_extdir}
  %%{xmldir} - by %%{pecl_xmldir}
- Remove defines of xmldir, peardir.
- Add 3 recommended macroses from doc http://fedoraproject.org/wiki/Packaging/PHP : php_apiver, __pecl, php_extdir

* Sat Dec 20 2008 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] spb [ dOt.] su> - 2.2.1-1
- Step to version 2.2.1
- As prepare to push it into Fedora:
 - Change release to 1%%{?dist}
 - Set setup quiet
 - Escape all %% in changelog section
 - Delete dot from summary
 - License change from real "PHP License" to BSD (by example with php-peck-phar and php-pecl-xdebug)
- %%defattr(-,root,root,-) changed to %%defattr(-,root,root,-)

* Mon May 12 2008 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] spb [ dOt.] su> - 2.2.0b2-0.Hu.0
- Step to version 2.2.0b2
- %%define peclName imagick and replece to it all direct appearances.

* Thu Mar 6 2008 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] info> - 2.1.1RC1-0.Hu.0
- Steep to version 2.1.1RC1 -0.Hu.0
- Add Hu-part and %%{?dist} into Release
- Add BuildRequires: ImageMagick-devel

* Fri Oct 12 2007 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] info> - 2.0.0RC1
- Global rename from php-pear-imagick to php-pecl-imagick. This is more correct.

* Wed Aug 22 2007 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] info> - 2.0.0RC1
- Initial release. (Re)Written from generated (pecl make-rpm-spec)
