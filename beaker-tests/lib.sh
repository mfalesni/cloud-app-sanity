function use()
{
  [ ! -e "${1}" ] && {
    URL="`cat config | grep \"^use ${1}:\" | sed -r -e \"s/^[^:]+://\"`"
    FOUND="`echo \"$URL\" | wc -l`"
    if [ $FOUND == "1" ] ; then
      ./git_download.sh "${1}" "${URL}"
      if [ $? -ne 0 ] ; then
        echo "Download of lotr failed!"
        exit 1
      fi
    else
      echo "use ${1} not found!"
      exit 1
    fi
    [ -n "${2}" ] &&  [ "${2}" == "x" ] && chmod +x "${1}"
  }
}
